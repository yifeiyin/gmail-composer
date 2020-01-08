import json
import time

def object_to_json(o):
    return json.dumps(o, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

def json_to_object(s):
    return json.loads(s)

def get_file_content(path):
    s = None
    with open(path) as f:
        s = f.readlines()
    if s is None:
        raise Exception('File content not found')
    return '\n'.join(s)

def generate_timestamp():
    t = time.localtime()

    return f'{t.tm_year}-{_pad2(t.tm_mon)}-{_pad2(t.tm_mday)}_{_pad2(t.tm_hour)}-{_pad2(t.tm_min)}-{_pad2(t.tm_sec)}'

def _pad2(v):
    return '0' + str(v) if v < 10 else str(v)