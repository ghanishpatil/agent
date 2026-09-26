import requests, time, re

base = 'https://outofcontext-app.onrender.com'

def login():
    for a in range(8):
        s = requests.Session()
        s.post(base + '/login', data={'username': 'compliance_officer', 'password': 'AuditPolicy2026!'}, timeout=40)
        if s.cookies.get('session'):
            return s
        time.sleep(25)
    return None

s = login()

def get(p, sess=True):
    cli = s if sess else requests
    for a in range(6):
        try:
            r = cli.get(base + p, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        return r.status_code, r.text
    return 'TR', ''

targets = ['/static/css/style.css', '/login', '/dashboard', '/settings', '/profile',
           '/templates', '/static/js/editor.js']
kw = re.compile(r'(editor|password|passwd|pwd|cred|secret|specialist|Policy2026|:\s*\S+2026)', re.I)
for p in targets:
    sc, body = get(p)
    print('====', p, sc, 'len', len(body))
    # comments
    for m in re.finditer(r'<!--(.*?)-->', body, re.S):
        print('  COMMENT:', m.group(1).strip()[:200])
    for m in re.finditer(r'/\*(.*?)\*/', body, re.S):
        c = m.group(1).strip()
        if kw.search(c):
            print('  CSSCOMMENT:', c[:200])
    # any line mentioning editor/password
    for line in body.splitlines():
        if kw.search(line) and ('editor' in line.lower() or 'password' in line.lower() or 'Policy2026' in line):
            print('  LINE:', line.strip()[:160])
    time.sleep(1)
