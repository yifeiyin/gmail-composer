import csv
from utilities import *

def load_persons_from_csv(file_path):
    result = []
    with open(file_path) as file:
        persons = csv.reader(file)
        for person in persons:
            result.append({
                'name': person[0],
                'email': person[1],
                'team': person[2],
                'leader': person[3]
            })
    return result


def format_template(template, details, fields):
    """
    Args:
        template: string
        details: dict
        fields: list of string
    Returns:
        A formatted string
    """
    for field in fields:
        looking_for = f'<<{field}>>'
        replace_with = details[field]
        template = template.replace(looking_for, replace_with)
    return template


def main():
    persons = load_persons_from_csv('secrets/2020Test.csv')
    common_fields = json_to_object(get_file_content('templates/common-fields.json'))
    timestamp = generate_timestamp()

    final_emails = []
    for person in persons:
        email = {}
        email['subject_line'] = common_fields['subject_line']
        email['from'] = '021chinese.group@gmail.com'
        email['to'] = person['email']

        email_body_preprocessed = get_file_content('templates/email-body.txt')
        email['email_body_content'] = format_template(
            email_body_preprocessed,
            {**common_fields, **person},
            ['name', 'team', 'leader']
        )
        final_emails.append(email)

    final_object = {}
    final_object['emails'] = final_emails
    final_object['tag'] = f'v1_{timestamp}'

    final_string = object_to_json(final_object)

    print('Final output is:')
    print(final_string)

    output_file_path = f'dist/{timestamp}.json'
    with open(output_file_path, 'w+') as f:
        f.write(final_string)

    print(f'It has been written to {output_file_path}')

# subject_line
# from
# to
# email_body_content



if __name__ == '__main__':
    main()
