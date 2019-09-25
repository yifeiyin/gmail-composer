import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pprint import pprint

from api import create_draft, create_message

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

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


def show_labels(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            pprint(label)

def main():
    service = get_service()
    if service is None:
        print('Did not get service')
        return

    message = create_message('test@gmail.com', 'yifeiyin@foxmail.com', '123123 subject 123123', 'Message')
    create_draft(service, 'me', message)

if __name__ == '__main__':
    main()
