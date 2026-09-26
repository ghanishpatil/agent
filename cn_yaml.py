import requests, re, json, sys
BASE='http://15.252.91.100'
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
s.cookies.update(json.load(open('cn_cookies.json')))
def csrf(h): 
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"',h); return m.group(1) if m else None

def submit(yaml_text):
    r=s.get(BASE+'/import/config/'); t=csrf(r.text)
    r=s.post(BASE+'/import/config/', data={'csrfmiddlewaretoken':t,'yaml_config':yaml_text}, headers={'Referer':BASE+'/import/config/'})
    body=re.sub(r'<style[\s\S]*?</style>','',r.text); body=re.sub(r'<[^>]+>',' ',body); body=re.sub(r'[ \t]+',' ',body)
    # show result region (after 'Parse')
    print('STATUS',r.status_code)
    # find result/alert/pre blocks in raw
    for m in re.finditer(r'(alert[\s\S]{0,400}?</div>|<pre[\s\S]*?</pre>)', r.text):
        seg=re.sub(r'<[^>]+>',' ',m.group(0)); seg=re.sub(r'\s+',' ',seg).strip()
        if seg: print('RESULT:', seg[:600])
    return r

cfg=sys.argv[1] if len(sys.argv)>1 else """workspace:
  name: Production
  theme: dark
features:
  import_url: true
  svg_preview: true
notifications:
  email: me@company.com
"""
submit(cfg)
# then re-check profile
r=s.get(BASE+'/api/profile/'); print('PROFILE after:', r.text)
