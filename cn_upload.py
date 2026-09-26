import requests, re, json, base64
BASE='http://15.252.91.100'
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
s.cookies.update(json.load(open('cn_cookies.json')))

# 1) full upload page text + any static js
r=s.get(BASE+'/upload/')
body=re.sub(r'<style[\s\S]*?</style>','',r.text)
txt=re.sub(r'<[^>]+>',' ',body); txt=re.sub(r'[ \t]+',' ',txt)
print('=== UPLOAD PAGE ===')
print(txt[:2500])
js=re.findall(r'(?:src|href)="([^"]+\.js[^"]*)"', r.text)
print('JS files:', js)

# 2) dashboard full text
r=s.get(BASE+'/dashboard/')
body=re.sub(r'<style[\s\S]*?</style>','',r.text); txt=re.sub(r'<[^>]+>',' ',body); txt=re.sub(r'[ \t]+',' ',txt)
print('\n=== DASHBOARD ===')
print(txt[:2500])

# 3) search all pages for public key / BEGIN, and static references
for p in ['/','/dashboard/','/files/','/upload/','/import/config/','/login/']:
    r=s.get(BASE+p)
    for m in re.finditer(r'(BEGIN [A-Z ]+KEY|jwks|public.?key|\.pem|/static/[^"\' ]+)', r.text, re.I):
        print(p,'REF:',m.group(0))
