import requests, time

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

paths = [
    '/api', '/api/', '/api/templates', '/api/templates/', '/api/templates/1', '/api/templates/3',
    '/api/render', '/api/documents', '/api/document', '/api/preview', '/api/assemble',
    '/api/user', '/api/users', '/api/me', '/api/profile', '/api/session', '/api/whoami',
    '/api/config', '/api/settings', '/api/audit', '/api/logs', '/api/flag', '/api/key',
    '/api/access-key', '/api/accesskey', '/api/templates/preview',
    '/api/v1/templates/preview', '/api/templates/render', '/api/templates/3/preview',
]

def get(p, method='GET'):
    for a in range(6):
        try:
            r = s.request(method, base + p, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        return r.status_code, r.headers.get('Allow', ''), r.headers.get('content-type', '')[:20], r.text[:120]
    return 'TR', '', '', ''

for p in paths:
    sc, allow, ct, body = get(p)
    if sc != 404:
        print('***', p, sc, 'Allow=' + allow, ct, body[:90])
    else:
        print('   ', p, sc)
    time.sleep(0.8)
