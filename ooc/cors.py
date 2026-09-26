import requests, time

base = 'https://outofcontext-app.onrender.com'

def req(method, path, headers=None, data=None):
    for a in range(6):
        try:
            r = requests.request(method, base + path, headers=headers or {}, data=data, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        return r
    return None

# OPTIONS preflight with a null origin
r = req('OPTIONS', '/api/templates/preview', headers={
    'Origin': 'null',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'content-type'
})
if r is not None:
    print('OPTIONS status', r.status_code)
    for k, v in r.headers.items():
        if 'access-control' in k.lower() or 'allow' in k.lower() or 'vary' in k.lower():
            print('  ', k, ':', v)
else:
    print('OPTIONS transient')

# GET preview (wrong method) to see allowed methods
r2 = req('GET', '/api/templates/preview')
if r2 is not None:
    print('GET status', r2.status_code, 'Allow:', r2.headers.get('Allow', ''))

# re-fetch login page, print all HTML comments
r3 = req('GET', '/login')
if r3 is not None:
    import re
    for m in re.finditer(r'<!--(.*?)-->', r3.text, re.S):
        print('COMMENT:', m.group(1).strip()[:200])
