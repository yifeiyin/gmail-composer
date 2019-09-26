import json

def object_to_json(o):
    return json.dumps(o, sort_keys=True, indent=4, separators=(',', ': '))

def json_to_object(s):
    return json.loads(s)

def get_file_content(path):
    s = None
    with open(path) as f:
        s = f.readlines()
    if s is None:
        raise Exception('File content not found')
    return '\n'.join(s)