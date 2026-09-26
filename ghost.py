import requests, re

BASE = 'https://ghostpanel-ctf.onrender.com'
s = requests.Session()

def clean(html):
    t = re.sub(r'<script.*?</script>', '', html, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', t).strip()

r = s.get(BASE, timeout=20)
flags = re.findall(r'CHAKRA\{[^}]+\}', r.text)
comments = re.findall(r'<!--(.*?)-->', r.text, re.S)
scripts = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', r.text)
print('FLAGS:', flags)
print('COMMENTS:', [c.strip()[:120] for c in comments])
print('SCRIPTS:', scripts)
print('TEXT:', clean(r.text)[:800])
print()

# Aggressive path recon
paths = [
    '/robots.txt', '/.env', '/admin', '/login', '/dashboard', '/panel',
    '/flag', '/flag.txt', '/secret', '/backup', '/api', '/api/flag',
    '/api/secret', '/api/admin', '/api/users', '/api/keys',
    '/config', '/config.php', '/config.js', '/config.json',
    '/.git/HEAD', '/.git/config', '/source', '/src',
    '/debug', '/test', '/dev', '/old', '/legacy',
    '/ghost', '/ghost/admin', '/v1', '/v2',
    '/static/flag.txt', '/public/flag.txt',
    '/admin/flag', '/admin/secret', '/admin/config',
    '/internal', '/private', '/hidden',
    '/api/v1/flag', '/api/v1/secret', '/api/v2/flag',
    '/phpinfo.php', '/info.php', '/server-info',
]

for p in paths:
    try:
        r2 = s.get(BASE + p, timeout=8, allow_redirects=True)
        if r2.status_code == 200 and len(r2.text) > 20:
            flags2 = re.findall(r'CHAKRA\{[^}]+\}', r2.text)
            txt = clean(r2.text)[:150]
            print(f'[200] {p}: {txt}')
            if flags2: print('  *** FLAG:', flags2)
        elif r2.status_code in [301, 302, 403]:
            print(f'[{r2.status_code}] {p} -> {r2.headers.get("Location","")}')
    except: pass
