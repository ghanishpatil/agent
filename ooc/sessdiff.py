import requests, time, flask_unsign as fu

base = 'https://outofcontext-app.onrender.com'

def login():
    for a in range(8):
        s = requests.Session()
        s.post(base + '/login', data={'username': 'compliance_officer', 'password': 'AuditPolicy2026!'}, timeout=40)
        if s.cookies.get('session'):
            return s
        time.sleep(25)
    return None

s = login()

def dump(label):
    c = s.cookies.get('session')
    try:
        d = fu.decode(c) if c else None
    except Exception:
        d = 'undecodable'
    print(label, '->', d)

dump('after-login')
# actions that might write session
s.get(base + '/templates', params={'q': 'INJECTMARKER', 'category': 'Legal & Compliance'}, timeout=40)
dump('after-search')
s.get(base + '/settings', timeout=40)
dump('after-settings')
s.get(base + '/profile', timeout=40)
dump('after-profile')
# denied editor (sets flash)
s.get(base + '/templates/3/edit', timeout=40, allow_redirects=True)
dump('after-denied-edit')
# denied preview api (sets flash?)
import base64
s.post(base + '/api/templates/preview', json={'content_b64': base64.b64encode(b'x').decode(), 'context': {}}, timeout=40)
dump('after-denied-preview')
