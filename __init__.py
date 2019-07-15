import logging
import json
import threading

import requests
from flask import Flask, request, jsonify

import remedyondemand as rod
import googlesheets as gs
import slack
import config

app = Flask(__name__)
app.url_map.strict_slashes = False
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
appreciate_employee = gs.appreciate_employee  # Google Sheets backend for nominating employees


def thx4that_command(user_info, user_input=None, token=None, channel_id=None, response_url=None, dry_run=False):
    if not user_input:
        if not dry_run:
            pass  # hook into Remedy On Demand
        params = {
            "channel": channel_id,
            "token": token,
            "attachments": [
                {
                    "text": "Who would you like to recognize?",
                    "fallback": "Use the following command /thx4that <employees email> <Reason you are recognize them.>.",
                    "color": "0ba7d7",
                    "attachment_type": "default",
                    "callback_id": "select_employee-{0}".format(slack.get_user_id(user_info)),
                    "actions": [
                        {
                            "name": "employee_list",
                            "text": "Choose a co-worker?",
                            "type": "select",
                            "data_source": "users"
                        }
                    ]
                }
            ]
        }
        headers = {
            "Content-Type": "application/json"
        }
        resp = requests.post(response_url, json=params, headers=headers)
        return True
    else:
        target_employee = user_input.split(" ")[0]
        reason = " ".join(user_input.split(" ")[1:])
        user_name = slack.get_user_real_name(user_info=user_info)
        message = '{0} recognized {1} for "{2}"'.format(user_name, target_employee, reason)
        logger.info(message)
        if not dry_run:
            # TODO: Respond with a callback_uri at a later time.
            # https://api.slack.com/slash-commands#triggering_a_command
            # Use requests to respond
            # hook into Remedy On Demand
            params = {
                "token": token,
                "channel": channel_id,
                "text": message
            }
            headers = {
                "Content-Type": "application/json"
            }
            # "Content-Type": "application/x-www-form-urlencoded"
            resp = requests.post(response_url, json=params, headers=headers)
            logger.info(resp)
            if target_employee.startswith("@"):
                target_employee = slack.get_user_info(user_name=target_employee)
            resp = appreciate_employee(user_info, target_employee, reason)
            logger.debug(resp)
        return message


@app.route("/")
def status():
    return 'OK'


@app.route("/dynamic-echo", methods=['POST'])
def dyanmic_echo():
    print request.form
    print json.loads(request.form['payload']).get("value")
    reason = json.loads(request.form['payload']).get("value", "")
    return jsonify({
        "options": [
            {
                "text": reason,
                "value": reason  # .lower().replace(" ", "_")
            }]
    })


@app.route("/interactive-messages", methods=['POST'])
def interactive_messages():
    """
    The final response should be and attachment with two sub fields saying that the successfully submitted for that user.
    """
    print request.form
    employee = ""
    payload = json.loads(request.form['payload'])
    login_id = payload.get("callback_id").split("-")[1]
    if len(payload.get("actions", [])) > 0 and payload.get('callback_id').startswith("select_reason"):
        employee_id = payload.get("callback_id").split("-")[2]
        employee_info = slack.get_user_info(user_id=employee_id)
        employee_name = slack.get_user_real_name(user_id=employee_id, user_info=employee_info)
        employee_email = slack.get_user_email(user_id=employee_id, user_info=employee_info)
        login_info = slack.get_user_info(user_id=login_id)
        login_id_email = slack.get_user_email(user_info=login_info)
        reason = payload.get("actions", [{}])[0].get("selected_options", [{}])[0].get("value")
        message = 'You have successfully recognized {1} for "{0}"'.format(reason, employee_name)
        logger.info(message)

        thread = threading.Thread(name='appreciate_employee',
                                  target=appreciate_employee,
                                  args=(login_info, employee_info, reason))
        thread.setDaemon(True)
        thread.start()
        logger.info("Daemon thread started for appreciate_employee {0}:{1}:{2}...".format(login_id_email, employee_email, reason))
        return message

    if payload.get('callback_id').startswith("select_employee"):
        employee_id = payload.get("actions", [{}])[0].get("selected_options", [{}])[0].get("value")
        employee = {"id": employee_id}
    return jsonify({
        "attachments": [
            {
                "text": "Why would you like to recognize them?",
                "fallback": "Upgrade your Slack client to use messages like these.",
                "color": "0ba7d7",
                "attachment_type": "default",
                "callback_id": "select_reason-{1}-{0}".format(employee.get("id"), login_id),
                "actions": [
                    {
                        "name": "reason_list",
                        "text": "What did they do?",
                        "type": "select",
                        "data_source": "external",
                        "min_query_length": 1,
                    }
                ]
            }]
    })


@app.route("/slash-command", methods=['POST'])
def slash_command():
    print request.form

    user_input = request.form.get('text')
    user_id = request.form.get('user_id')
    channel_id = request.form.get('channel_id')
    user_info = slack.get_user_info(user_id=user_id)
    token = request.form.get('token')
    response_url = request.form.get('response_url')

    thread = threading.Thread(name='thx4that_command',
                              target=thx4that_command,
                              args=(user_info, user_input),
                              kwargs={'channel_id': channel_id, 'token': token, 'response_url':response_url})
    thread.setDaemon(True)
    thread.start()
    logger.info("Daemon thread started...")

    return "", 200, {'Content-Type': 'application/json'}


@app.route("/_ah/health")
def healthcheck():
    return 'OK'
