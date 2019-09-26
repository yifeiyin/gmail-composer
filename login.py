import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pprint import pprint

from api import *
from utilities import *

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.modify'
]

def get_service():
    """Returns the service object
    """
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('secrets/token.pickle'):
        with open('secrets/token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('secrets/credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('secrets/token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    service = build('gmail', 'v1', credentials=credentials)
    return service


def get_labels(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    return labels


def create_label(service, new_label_name):
    # Doc https://developers.google.com/gmail/api/v1/reference/users/labels/create
    # Add label to draft https://stackoverflow.com/questions/26578710/add-a-label-to-a-draft
    existing = find_label_by_name(service, new_label_name)
    if (existing is not None):
        print(f"Label {new_label_name} already exists")
        return existing

    new_label_object = label = {'messageListVisibility': 'show', 'name': new_label_name, 'labelListVisibility': 'labelShow' }
    label = service.users().labels().create(userId='me', body=new_label_object).execute()
    return label['id']


def find_label_by_name(service, name):
    labels = get_labels(service)
    labels = list(filter(lambda x: x['name'] == name, labels))
    if (len(labels) == 0):
        return None
    elif (len(labels) == 1):
        return labels[0]['id']
    else:
        print(f'WARNING: More than one label found: {labels}')
        return labels[0]['id']


def main():
    service = get_service()

    if service is None:
        print('Did not get service')
        return

    # message = create_message('test@gmail.com', 'yifeiyin@foxmail.com', '测试标题', '<b>1aaaxxx</b>')
    # draft_created = create_draft(service, 'me', message)
    # add_label_to_message(service, 'me', draft_created['message']['id'], create_label(service, 'testLabel111'))

    file_name = input('file_name? ')
    file_path = f'dist/{file_name}.json'
    info_read = json_to_object(get_file_content(file_path))
    tag = info_read['tag']
    emails = info_read['emails']

    for email in emails:
        message = create_message(email['from'], email['to'], email['subject_line'], email['email_body_content'])
        draft = create_draft(service, 'me', message)
        add_label_to_message(service, 'me', draft['message']['id'], create_label(service, tag))
        print(f"Draft created. For {email['to']}, with id {draft['message']['id']}, tagged {tag}")

if __name__ == '__main__':
    main()
