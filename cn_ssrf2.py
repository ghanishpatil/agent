import requests, re, json, time, hashlib, hmac, base64, urllib.parse, sys
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://15.252.91.100'
st=json.load(open('cn_state.json'))
S=requests.Session(); S.headers.update({'User-Agent':'Mozilla/5.0'})
for k,v in st['cookies'].items(): S.cookies.set(k,v)

def csrf(h):
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"',h); return m.group(1) if m else None

def import_url(url, show=True):
    r=S.get(BASE+'/import/url/')
    if r.status_code!=200 or 'Administrator' in r.text:
        print('[!] import/url not accessible', r.status_code); print(r.text[:200]); return None
    t=csrf(r.text)
    # find the field name for the url
    fields=re.findall(r'<input[^>]*name="([^"]+)"',r.text)+re.findall(r'<textarea[^>]*name="([^"]+)"',r.text)
    data={'csrfmiddlewaretoken':t}
    urlfield=[f for f in fields if f not in ('csrfmiddlewaretoken',) and ('url' in f.lower() or 'source' in f.lower())]
    uf=urlfield[0] if urlfield else 'url'
    data[uf]=url
    r=S.post(BASE+'/import/url/', data=data, headers={'Referer':BASE+'/import/url/'})
    if show:
        # extract result blocks
        for m in re.finditer(r'(class="alert[^"]*"[\s\S]{0,800}?</div>|<pre[\s\S]*?</pre>)', r.text):
            seg=re.sub(r'<[^>]+>',' ',m.group(0)); seg=re.sub(r'\s+',' ',seg).strip()
            seg=seg.replace('&#x27;',"'").replace('&quot;','"').replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
            if seg and 'Paste' not in seg: print('   >',seg[:700])
    return r

# first: view the import/url page to learn the field + hints
r=S.get(BASE+'/import/url/')
print('[*] import/url page status', r.status_code)
body=re.sub(r'<style[\s\S]*?</style>','',r.text); txt=re.sub(r'<[^>]+>',' ',body); txt=re.sub(r'[ \t]+',' ',txt)
print(txt[:1200])
print('--- comments ---')
for c in re.findall(r'<!--(.*?)-->', r.text, re.S): print('  //', c.strip())
print('--- input fields ---', re.findall(r'<input[^>]*name="([^"]+)"',r.text), re.findall(r'<textarea[^>]*name="([^"]+)"',r.text))
