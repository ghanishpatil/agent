import requests

BASE = 'https://outfjord-your-notes-1860d6ea0037.chall.nnsc.tf'
s = requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0'})

# Check headers / CSP on main page and note
r = s.get(BASE + '/', timeout=15)
print('=== / headers ===')
for k,v in r.headers.items():
    print(f'  {k}: {v}')

# theme.css with type css import - check if it sets Content-Type text/css strictly
r2 = s.get(BASE + '/theme.css?name=aurora', timeout=15)
print('\n=== theme.css headers ===')
for k,v in r2.headers.items():
    print(f'  {k}: {v}')

# Look for admin bot / report endpoint hints, other routes
for p in ['/api', '/admin', '/bot', '/report', '/flag', '/api/note', '/theme.css']:
    rr = s.get(BASE+p, timeout=10)
    print(f'{p}: [{rr.status_code}] {rr.headers.get("Content-Type")} len={len(rr.text)}')
