import requests, re, json

BASE = 'https://ashen-checkpoint-challenge--yoriichi13.replit.app'
s = requests.Session()

def clean(html):
    t = re.sub(r'<script.*?</script>', '', html, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', t).strip()

r = s.get(BASE, timeout=20)
print('Status:', r.status_code)
flags = re.findall(r'CHAKRA\{[^}]+\}|flag\{[^}]+\}', r.text, re.I)
print('FLAGS:', flags)
comments = re.findall(r'<!--(.*?)-->', r.text, re.S)
print('COMMENTS:', [c.strip()[:100] for c in comments])
scripts = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', r.text)
print('SCRIPTS:', scripts)
print('TEXT:', clean(r.text)[:1000])

# API recon
for p in ['/api', '/api/chain', '/api/blocks', '/api/branch', 
          '/chain', '/blocks', '/branch', '/checkpoint',
          '/api/checkpoint', '/submit', '/api/submit',
          '/witness', '/api/witness', '/nonce', '/proof',
          '/robots.txt', '/.env', '/source']:
    try:
        r2 = s.get(BASE + p, timeout=8)
        if r2.status_code == 200 and len(r2.text) > 10:
            flags2 = re.findall(r'CHAKRA\{[^}]+\}', r2.text)
            print(f'[200] {p}: {clean(r2.text)[:200]}')
            if flags2: print('  FLAG:', flags2)
        elif r2.status_code not in [404, 405]:
            print(f'[{r2.status_code}] {p}')
    except: pass
