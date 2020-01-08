# Gmail api related imports
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors

# Email related imports
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os


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



def create_draft(service, user_id, message_body):
    """Create and insert a draft email. Print the returned draft's message and id.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message_body: The body of the email message, including headers.

    Return draft object, including draft id and message meta data.
    """

    message = { 'message': message_body }
    draft = service.users().drafts().create(userId=user_id, body=message).execute()

    print("Draft id: {}\nDraft message: {}".format(draft['id'], draft['message']))

    return draft


def add_label_to_message(service, user_id, message_id, label):
    # See doc at https://developers.google.com/gmail/api/v1/reference/users/messages/modify
    message_labels = { 'removeLabelIds': [], 'addLabelIds': [label] }
    message = service.users().messages().modify(userId = user_id, id = message_id, body = message_labels).execute()
    label_id = message['labelIds'][0]
    print(f"Message {message_id} now has a label with id {label_id}")
    return label_id


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text, 'html')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return { 'raw': raw }


def create_message_with_attachment(sender, to, subject, message_text, file_dir, filename):
    """Create a message for an email.
    Args:
        sender: The email address of the sender.
        to: The email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file_dir: The directory containing the file to be attached.
        filename: The name of the file to be attached.

    Return an object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    path = os.path.join(file_dir, filename)
    content_type, encoding = mimetypes.guess_type(path)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)

    if main_type == 'text':
        fp = open(path, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()

    elif main_type == 'image':
        fp = open(path, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()

    elif main_type == 'audio':
        fp = open(path, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()

    else:
        fp = open(path, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}

