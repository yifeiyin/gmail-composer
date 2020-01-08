from api import *
from utilities import *

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
