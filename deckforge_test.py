import requests, re, io, zipfile

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

def render(html):
    r = s.post(BASE + '/html-to-image', json={'pages': [html]}, timeout=40)
    return r

# Test 1: basic render works?
html = '<h1 style="font-size:80px;color:red">HELLO TEST</h1>'
r = render(html)
print('Basic render:', r.status_code, r.headers.get('Content-Type'), 'len=', len(r.content))
if r.status_code != 200:
    print('Error:', r.text[:500])

# Save output to inspect
if r.status_code == 200:
    with open('f:/mission-git-hackss/mission-git-hackss/deck_out.zip', 'wb') as f:
        f.write(r.content)
    # try unzip
    try:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        print('ZIP contents:', z.namelist())
    except Exception as e:
        print('Not a zip:', e)
        print('First bytes:', r.content[:20])
