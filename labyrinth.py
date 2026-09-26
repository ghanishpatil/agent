import requests, re, base64, codecs

BASE = 'https://chakravyuh-ctf-challenge.onrender.com'
s = requests.Session()

def clean(html):
    t = re.sub(r'<script.*?</script>', '', html, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', t).strip()

r = s.get(BASE, timeout=20)
print('=== HOME ===')
flags = re.findall(r'CHAKRA\{[^}]+\}', r.text)
print('FLAGS:', flags)
comments = re.findall(r'<!--(.*?)-->', r.text, re.S)
print('COMMENTS:', [c.strip()[:100] for c in comments])
scripts = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', r.text)
print('SCRIPTS:', scripts)
print('TEXT:', clean(r.text)[:1000])
print()

# robots, common paths
for p in ['/robots.txt', '/sitemap.xml', '/.env', '/admin', '/flag', '/secret', '/api', '/tier1', '/tier2', '/tier3', '/level1', '/level2', '/level3']:
    r2 = s.get(BASE + p, timeout=8)
    if r2.status_code == 200 and len(r2.text) > 20:
        flags2 = re.findall(r'CHAKRA\{[^}]+\}', r2.text)
        print(f'[200] {p}: {clean(r2.text)[:200]}')
        if flags2: print('  FLAGS:', flags2)
    elif r2.status_code not in [404, 405]:
        print(f'[{r2.status_code}] {p}')
