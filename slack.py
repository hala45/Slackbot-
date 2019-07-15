import json
import logging

import requests
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_list(user_filter):
    '''
    ref: https://slack.com/api/users.list
    '''
    params = {
        "token": config.SLACK_TOKEN,
        "presence": "false"
    }
    resp = requests.post("https://slack.com/api/users.list", data=params)
    logger.debug(resp.content)
    filtered_resp = [x for x in resp.json().get("members") if user_filter(x)]
    return filtered_resp


def get_user_info(user_id=None, user_name=None):
    '''
    ref: https://slack.com/api/users.info
    '''
    if user_name is not None:
        user_info = get_user_list(lambda x: x['name'] == user_name.replace("@", "")).pop()
        return {"user": user_info}
    params = {
        "token": config.SLACK_TOKEN,
        "user": user_id
    }
    resp = requests.post("https://slack.com/api/users.info", data=params)
    logger.debug(resp.content)
    return resp.json()

def get_user_id(user_info):
    '''
    ref: https://slack.com/api/users.info
    '''
    return user_info.get('user', {}).get('id')

def get_user_name(user_id=None, user_name=None, user_info=None):
    '''
    ref: https://slack.com/api/users.info
    '''
    if user_name is not None:
        user_info = get_user_info(user_name=user_name)
    else:
        user_info = user_info if user_info else get_user_info(user_id)
    return user_info.get('user', {}).get('name')


def get_user_real_name(user_id=None, user_name=None, user_info=None):
    '''
    ref: https://slack.com/api/users.info
    '''
    if user_name is not None:
        user_info = get_user_info(user_name=user_name)
    else:
        user_info = user_info if user_info else get_user_info(user_id)
    real_name = user_info.get('user', {}).get('profile', {}).get('real_name').title()
    return real_name


def get_user_email(user_id=None, user_name=None, user_info=None):
    '''
    ref: https://slack.com/api/users.info
    '''
    if user_name is not None:
        user_info = get_user_info(user_name=user_name)
    else:
        user_info = user_info if user_info else get_user_info(user_id)
    return user_info.get('user', {}).get('profile', {}).get('email')


def get_channel_name(channel_id):
    '''
    ref: https://api.slack.com/methods/channels.info
    '''
    params = {
        "token": config.SLACK_TOKEN,
        "channel": channel_id
    }
    resp = requests.post("https://slack.com/api/channels.info", data=params)
    logger.info(resp.content)
    return resp.json().get('channel_name')


def post_message(channel_id, message, token=None):
    """
    ref: https://api.slack.com/methods/chat.postMessage
    """
    logger.info(channel_id)
    params = {
        "token": config.SLACK_TOKEN,
        "channel": channel_id
    }
    if type(message) == dict:
        params["text"] = message.get("text")
        params["attachments"] = json.dumps(message.get("attachments"))
    else:
        params["text"] = message
    resp = requests.post("https://slack.com/api/chat.postMessage", data=params)
    logger.info(resp.content)
    return resp

if __name__ == '__main__':
    user_id = "U025QN6JL"
    post_message(user_id, "Congratulations you have been nominated in Thx4That.")
    message = {
        "text": "Congratulations you have been nominated in Thx4That.",
        "attachments": [
            {
                "fields": [{"title": "Nominated By", "value": "Dylan Roy"},
                           {"title": "Reason", "value": "Here is the reason that you have been nominated."}]
            }
        ]
    }
    post_message(user_id, message)
    print " [ Get Channel Name ] "
    print post_message("C5MVBQRK7", message)
    print "[ Get User List filtered by 'name' == dylan.roy ]"
    print get_user_list(lambda x: x['name'] == "dylan.roy")
    print "[ Get User Email By user_name ]"
    print get_user_email(user_name="@dylan.roy")
    user_info = get_user_info(user_id=user_id)
    print user_info
    print "[ Get User Email By user_id ]"
    print get_user_email(user_id=user_id)
    print get_user_name(user_id=user_id)
    print get_user_real_name(user_id=user_id)
    print get_user_email(user_id=user_id, user_info=user_info)
    print get_user_name(user_id=user_id, user_info=user_info)
    print get_user_real_name(user_id=user_id, user_info=user_info)
