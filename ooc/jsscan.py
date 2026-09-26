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
        return r.status_code, len(r.text), r.text
    return 'TRANSIENT', 0, ''

cands = [
    '/static/js/editor.js', '/static/js/app.js', '/static/js/preview.js', '/static/js/main.js',
    '/static/js/templatedesk.js', '/static/js/template.js', '/static/js/render.js',
    '/static/app.js', '/static/main.js', '/static/editor.js', '/static/js/index.js',
    '/static/js/live.js', '/static/js/dashboard.js', '/static/js/scripts.js',
]
for p in cands:
    sc, n, body = get(p)
    mark = ''
    if isinstance(sc, int) and sc == 200:
        low = body.lower()
        for kw in ['preview', 'render', 'fetch', 'xmlhttp', 'ajax', '/templates', '/api', 'post']:
            if kw in low:
                mark += kw + ','
    print(p, sc, n, mark)
    if isinstance(sc, int) and sc == 200 and n > 0:
        open(r'F:\mission-git-hackss\mission-git-hackss\ooc' + p.replace('/', '_'), 'w', encoding='utf-8').write(body)
    time.sleep(1.2)
