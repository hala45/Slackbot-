import logging

import requests

from config import REMEDY_DOMAIN, REMEDY_PROTOCOL, REMEDY_USERNAME, REMEDY_PASSWORD


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def authorize(dry_run=False):
    """Invoke the following REST API for getting the authorized token
        POST https://newscorp-qa-restapi.onbmc.com/api/jwt/login
        username : config.USERNAME
        password : config.PASSWORD
    """
    if dry_run:
        return "dry_run AR-JWT"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "username": REMEDY_USERNAME,
        "password": REMEDY_PASSWORD
    }
    resp = requests.post("{0}://{1}/api/jwt/login".format(REMEDY_PROTOCOL, REMEDY_DOMAIN), data=payload, headers=headers)
    try:
        logger.debug(resp.content)
        return resp.content
    except:
        logger.debug("Failed to authorize.")
        return False


def create_service_request(login_id, employee_email, jwt_token=None, dry_run=False):
    """
     2. Invoke the following REST API for Service Request creation
         POST       https://newscorp-qa-restapi.onbmc.com/api/arsys/v1/entry/SRM:RequestInterface_Create
         Headers
         Authorization - token value
         content-Type - application/json

       Body
       {
           "values" : {
             "z1D Action" : "CREATE" ,
             "Status" : "Submitted" ,
             "Login ID" : "shamhoon.jaffaree@dowjones.com",
             "Short Description" : "Thanx4That" ,
             "Details" : "Thanx4That",
             "Source Keyword" : "MyIT",
             "TitleInstanceID" : "SRGAA5V0F1Q68AOO6M3HONKN2F1L0H"
         }
        }
    """
    if dry_run:
        return {"values": {"Request Number": "REQ000000012716", "InstanceId": "AGGAA5V0F2ICBAOQ31BYOP7J4J9J8F"}, "_links": {"self": [{"href": "https: //newscorp-qa-restapi.onbmc.com/api/arsys/v1/entry/SRM: RequestInterface_Create/000000000004015"}]}}
    jwt_token = jwt_token if jwt_token else authorize(dry_run)
    headers = {
        "Authorization": "AR-JWT {0}".format(jwt_token),
        "Content-Type": "application/json"
    }
    payload = {
        "values": {
            "z1D Action": "CREATE",
            "Status": "Submitted",
            "Login ID": login_id,
            "Customer Login": employee_email,
            "Short Description": "Thx4That",
            "Details": "Thx4That",
            "Source Keyword": "MyIT",
            "TitleInstanceID": "SRGAA5V0F1Q68AOO6M3HONKN2F1L0H"
        }
    }
    resp = requests.post("{0}://{1}/api/arsys/v1/entry/SRM:RequestInterface_Create".format(REMEDY_PROTOCOL, REMEDY_DOMAIN), json=payload, headers=headers)
    if resp.ok:
        return resp.headers.get("Location").split("/")[-1]
    else:
        logger.info(resp.content)
        logger.info(resp.headers)
        return False


def get_service_request(request_id, jwt_token=None, dry_run=False):
    """
    3. Invoke the following REST API from the previous output to get Service Request ID
    GET https://newscorp-qa-restapi.onbmc.com/api/arsys/v1/entry/SRM:RequestInterface_Create/000000000004014?fields=values(Request Number, InstanceId)

    The output values will have
    {"values":{"Request Number":"REQ000000012716","InstanceId":"AGGAA5V0F2ICBAOQ31BYOP7J4J9J8F"},"_links":{"self":[{"href":"https://newscorp-qa-restapi.onbmc.com/api/arsys/v1/entry/SRM:RequestInterface_Create/000000000004015"}]}}
    """
    if dry_run:
        return {"values": {"Request Number": "REQ000000012716", "InstanceId": "AGGAA5V0F2ICBAOQ31BYOP7J4J9J8F"}, "_links": {"self": [{"href": "https: //newscorp-qa-restapi.onbmc.com/api/arsys/v1/entry/SRM: RequestInterface_Create/000000000004015"}]}}
    jwt_token = jwt_token if jwt_token else authorize(dry_run)
    headers = {
        "Authorization": "AR-JWT {0}".format(jwt_token),
        "Content-Type": "application/json"
    }
    resp = requests.get("{0}://{1}/api/arsys/v1/entry/SRM:RequestInterface_Create/{2}?fields=values(Request Number, InstanceId)".format(REMEDY_PROTOCOL, REMEDY_DOMAIN, request_id), headers=headers)
    logger.info(resp.content)
    return resp.json().get("values")


def get_service_requests(jwt_token=None, dry_run=False):
    jwt_token = jwt_token if jwt_token else authorize(dry_run)
    headers = {
        "Authorization": "AR-JWT {0}".format(jwt_token),
        "Content-Type": "application/json"
    }
    resp = requests.get("{0}://{1}/api/arsys/v1/entry/SRM:RequestInterface_Create".format(REMEDY_PROTOCOL, REMEDY_DOMAIN), headers=headers)
    return resp


def create_question_response(answer, instance_id, jwt_token=None, dry_run=False):
    """
    4.Invoke the following REST API for QuestionResponse creation ( you need to pass the Instance ID from the previous step into the SRInstanceID, the QuestionDef_InstanceID and QuestionSRD_Instance ID are passed with the value mentioned below, the appreciation details are passed in the Answer in Char field.
     POST       https://newscorp-qa-restapi.onbmc.com/api/arsys/v1/entry/SRD:MultipleQuestionResponse
    {
       "values" : {
         "SRInstanceID" : "AGGAA5V0F2ICBAOQ34CZOP72509JWH" ,
         "QuestionDef_InstanceID" : "QDGAA5V0F1Q68AOO88PSONM9OQ1PWC" ,
         "QuestionSRD_Instance ID" : "QSGAA5V0F1Q68AOO88PSONM9OQ1PWB",
         "Question Text" : "Tell us why you want to recognize your colleague: ",
         "QuestionOrder" : 1,
         "Commit Status" : 1,
         "AnswerFormat" : "TEXT",
         "Answer In Char" : "You are the best",
         "Answer Internal" : "You are the best",
         "Menu Label" : "You are the best"
     }
    }
    """
    if dry_run:
        return {"values": {"Request Number": "REQ000000012716", "InstanceId": "AGGAA5V0F2ICBAOQ31BYOP7J4J9J8F"}, "_links": {"self": [{"href": "https: //newscorp-qa-restapi.onbmc.com/api/arsys/v1/entry/SRM: RequestInterface_Create/000000000004015"}]}}
    jwt_token = jwt_token if jwt_token else authorize(dry_run)
    headers = {
        "Authorization": "AR-JWT {0}".format(jwt_token),
        "Content-Type": "application/json"
    }
    payload = {
        "values": {
            "SRInstanceID": instance_id,
            "QuestionDef_InstanceID": "QDGAA5V0F1Q68AOO88PSONM9OQ1PWC",
            "QuestionSRD_Instance ID": "QSGAA5V0F1Q68AOO88PSONM9OQ1PWB",
            "Question Text": "Tell us why you want to recognize your colleague: ",
            "QuestionOrder": 1,
            "Commit Status": 1,
            "AnswerFormat": "TEXT",
            "Answer In Char": answer,
            "Answer Internal": answer,
            "Menu Label": answer
        }
    }
    resp = requests.post("{0}://{1}/api/arsys/v1/entry/SRD:MultipleQuestionResponse".format(REMEDY_PROTOCOL, REMEDY_DOMAIN), json=payload, headers=headers)
    return resp


def get_question_responses(jwt_token=None, dry_run=False):
    jwt_token = jwt_token if jwt_token else authorize(dry_run)
    headers = {
        "Authorization": "AR-JWT {0}".format(jwt_token),
        "Content-Type": "application/json"
    }
    resp = requests.get("{0}://{1}/api/arsys/v1/entry/SRD:MultipleQuestionResponse".format(REMEDY_PROTOCOL, REMEDY_DOMAIN), headers=headers)
    return resp


def get_question_response(instance_id, jwt_token=None, dry_run=False):
    jwt_token = jwt_token if jwt_token else authorize(dry_run)
    headers = {
        "Authorization": "AR-JWT {0}".format(jwt_token),
        "Content-Type": "application/json"
    }
    resp = requests.get("{0}://{1}/api/arsys/v1/entry/SRD:MultipleQuestionResponse/{2}".format(REMEDY_PROTOCOL, REMEDY_DOMAIN, instance_id), headers=headers)
    return resp


def appreciate_employee(login_id, employee_email, reason, dry_run=False):
    logger.info("login_id:{0} Email:{1} Reason:{2} Dry Run:{3}".format(login_id, employee_email, reason, dry_run))
    request_id = create_service_request(login_id, employee_email, dry_run=dry_run)
    logger.info("Request ID:{0}".format(request_id))
    values = get_service_request(request_id, dry_run=dry_run)
    instance_id = values.get("InstanceId")
    request_number = values.get("Request Number")
    return create_question_response(reason, instance_id, dry_run=dry_run)

if __name__ == '__main__':
    # resp = appreciate_employee("dylan.roy@dowjones.com", "dylan.roy@dowjones.com", "This is a test submission. Look here.")
    # resp = get_question_responses()
    resp = get_service_requests()
    # resp = get_question_response("000000000004080")
    print resp.content
    print resp.headers
