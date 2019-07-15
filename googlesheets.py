import os
import json
import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import slack


def credentials():
    scopes = ['https://www.googleapis.com/auth/drive', 'https://spreadsheets.google.com/feeds']
    google_credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.abspath('dj-dna-dowjones.json'), scopes)
    return google_credentials


def get_client():
    gc = gspread.authorize(credentials())
    return gc


def create_new_spreadsheet(title, parent_folder, client=get_client()):
    headers = {'Content-Type': 'application/json'}
    data = {
        'title': title,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'allowFileDiscovery': "true",
        'supportsTeamDrives': "true",
        'parents': [parent_folder]
    }
    r = client.session.post(
        gspread.urls.DRIVE_FILES_API_V2_URL,
        json.dumps(data),
        headers=headers
    )
    spreadsheet_id = r.json()['id']
    sh = client.open_by_key(spreadsheet_id)
    print sh.share('dowjones.com', perm_type='domain', role='reader')
    return sh


def appreciate_employee(nominator_info, nominee_info, reason, dry_run=False):
    """
    Nominations Sheet:
    1plUmyrM2tXUTL0H-_vAAc0mZyjw5NkhsEYFkVcIbimg
    """
    nominator = slack.get_user_real_name(user_info=nominator_info)
    nominee = slack.get_user_real_name(user_info=nominee_info)
    nominator_email = slack.get_user_email(user_info=nominator_info)
    nominee_email = slack.get_user_email(user_info=nominee_info)
    nominee_id = slack.get_user_id(user_info=nominee_info)
    sh = get_client().open_by_key('1fBB0iWBkEsWWha2LA-ygHceis-SZGg6eFDF6Z-2DPNE')
    wks = None
    try:
        wks = sh.worksheet(datetime.datetime.today().strftime('%Y-%m'))
    except:
        wks = sh.add_worksheet(title=datetime.datetime.today().strftime('%Y-%m'), rows="1", cols="3")
        wks.update_cell(1, 1, 'Nominator')
        wks.update_cell(1, 2, 'Nominee')
        wks.update_cell(1, 3, 'Reason')
    wks.append_row([nominator_email, nominee_email, reason])
    # TODO: Post message to user and to the Thx4That channel
    channel_message_text = "{0} has been nominated in Thx4That.".format(nominee)
    message = {
        "text": "Congratulations you have been nominated in Thx4That.",
        "attachments": [
            {
                "fields": [{"title": "Nominated By", "value": nominator},
                           {"title": "Reason", "value": reason}]
            }
        ]
    }
    # Post personal message
    slack.post_message(nominee_id, message)
    # Post message to channel
    message['text'] = channel_message_text
    slack.post_message("C5MVBQRK7", message)

if __name__ == '__main__':
    user_info = slack.get_user_info(user_name="dylan.roy")
    print user_info
    appreciate_employee(user_info, user_info, "TEST: For some test reasons...")
