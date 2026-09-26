import requests, re

BASE = 'https://gokul-hidden-makhan.vercel.app'
s = requests.Session()

def clean(html):
    t = re.sub(r'<script.*?</script>', '', html, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', t).strip()

r = s.get(BASE, timeout=15)
flags = re.findall(r'CHAKRA\{[^}]+\}|CTF\{[^}]+\}|flag\{[^}]+\}', r.text, re.I)
comments = re.findall(r'<!--(.*?)-->', r.text, re.S)
scripts = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', r.text)
print('FLAGS:', flags)
print('COMMENTS:', [c.strip()[:100] for c in comments])
print('SCRIPTS:', scripts)
print('TEXT:', clean(r.text)[:500])

# standard recon
for p in ['/robots.txt', '/.env', '/flag', '/flag.txt', '/secret', '/makhan', '/krishna', '/hidden', '/admin', '/sitemap.xml']:
    r2 = s.get(BASE + p, timeout=8)
    if r2.status_code == 200 and len(r2.text) > 10:
        flags2 = re.findall(r'CHAKRA\{[^}]+\}|CTF\{[^}]+\}', r2.text, re.I)
        print(f'[200] {p}: {clean(r2.text)[:200]}')
        if flags2: print('  FLAG:', flags2)
    elif r2.status_code not in [404, 405]:
        print(f'[{r2.status_code}] {p}')

# fetch all JS files
for js in scripts:
    url = js if js.startswith('http') else BASE + ('/' if not js.startswith('/') else '') + js
    rj = s.get(url, timeout=8)
    if rj.status_code == 200:
        flags3 = re.findall(r'CHAKRA\{[^}]+\}|CTF\{[^}]+\}', rj.text, re.I)
        print(f'JS {js}: flags={flags3}')
        if flags3: print(rj.text[:500])
