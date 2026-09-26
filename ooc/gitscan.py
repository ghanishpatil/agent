import requests, time

base = 'https://outofcontext-app.onrender.com'
s = requests.Session()

def get(p):
    for a in range(6):
        try:
            r = s.get(base + p, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        return r.status_code, len(r.text), r.text[:150]
    return 'TR', 0, ''

paths = [
    '/.git/HEAD', '/.git/config', '/.git/index', '/.gitignore',
    '/app.py.bak', '/app.py~', '/main.py.bak', '/.env', '/.env.bak',
    '/backup.zip', '/source.zip', '/app.zip', '/dump.sql',
    '/sitemap.xml', '/.well-known/security.txt', '/static/', '/static/js/',
    '/static/js/editor.js.bak', '/requirements.txt', '/Dockerfile', '/docker-compose.yml',
]
for p in paths:
    sc, n, body = get(p)
    interesting = isinstance(sc, int) and sc == 200
    print(('***' if interesting else '   '), p, sc, n, (body[:80].replace('\n', ' ') if interesting else ''))
    time.sleep(0.7)
