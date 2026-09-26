import requests, re, base64

BASE = 'https://the-servers-secret3.vercel.app'
s = requests.Session()

def clean(html):
    t = re.sub(r'<script.*?</script>', '', html, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', t).strip()

# Hit both hidden paths and everything inside
paths = [
    '/restricted_archive_03/',
    '/admin_panel_internal/',
    '/restricted_archive_03/index.html',
    '/admin_panel_internal/index.html',
    '/restricted_archive_03/logs.txt',
    '/restricted_archive_03/secret.txt',
    '/restricted_archive_03/flag.txt',
    '/restricted_archive_03/sysadmin.log',
    '/admin_panel_internal/logs.txt',
    '/admin_panel_internal/secret.txt',
    '/admin_panel_internal/flag.txt',
]

for p in paths:
    r = s.get(BASE + p, timeout=10)
    if r.status_code == 200:
        flags = re.findall(r'CHAKRA\{[^}]+\}|flag\{[^}]+\}', r.text, re.I)
        print(f'[200] {p}')
        print(clean(r.text)[:500])
        if flags: print('FLAGS:', flags)
        print()
    else:
        print(f'[{r.status_code}] {p}')
