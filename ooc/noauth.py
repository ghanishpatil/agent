import requests, time, base64

base = 'https://outofcontext-app.onrender.com'
b64 = base64.b64encode(b'Hello {{7*7}} World').decode()
body = {'content_b64': b64, 'context': {}}

def call(cookie=None, label=''):
    h = {}
    if cookie is not None:
        h['Cookie'] = 'session=' + cookie
    for a in range(6):
        try:
            r = requests.post(base + '/api/templates/preview', json=body, headers=h, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        return label, r.status_code, r.text[:180]
    return label, 'TR', ''

# 1) no cookie at all (unauthenticated)
print(call(None, 'no-cookie'))
time.sleep(2)
# 2) garbage/empty session cookie
print(call('', 'empty-session'))
time.sleep(2)
print(call('garbage', 'garbage-session'))
