import requests, re, sys, json, base64
BASE='http://15.252.91.100'
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
# re-register to get fresh session
import random,string
def csrf(h): 
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"',h); return m.group(1) if m else None
def solve(h):
    q=re.search(r'class="captcha-question"[^>]*>(.*?)</',h,re.S); cid=re.search(r'name="captcha_id" value="([^"]*)"',h)
    if not q: return None,None
    m=re.search(r'(\d+)\s*([\+\-\*x×])\s*(\d+)',q.group(1))
    a,op,b=int(m.group(1)),m.group(2),int(m.group(3)); ans={'+':a+b,'-':a-b,'*':a*b,'x':a*b,'×':a*b}[op]
    return cid.group(1),ans
U='dfr'+''.join(random.choices(string.ascii_lowercase,k=7)); P='Passw0rd!zz'
r=s.get(BASE+'/register/'); t=csrf(r.text); cid,ans=solve(r.text)
s.post(BASE+'/register/',data={'csrfmiddlewaretoken':t,'username':U,'email':U+'@c.com','password':P,'captcha_id':cid,'captcha_answer':str(ans)},headers={'Referer':BASE+'/register/'})
print('user',U)

# decode JWT
jwt=s.cookies.get('cloudnine_access')
def b64d(x): return base64.urlsafe_b64decode(x+'='*(-len(x)%4))
if jwt:
    h,p,sig=jwt.split('.')
    print('JWT header:', b64d(h).decode())
    print('JWT payload:', b64d(p).decode())

for path in ['/dashboard/','/import/config/','/api/profile/','/files/','/upload/']:
    r=s.get(BASE+path)
    print('\n===== GET',path,r.status_code,'len',len(r.text),'=====')
    # strip css/scripts, show visible text and forms
    body=r.text
    forms=re.findall(r'<form[\s\S]*?</form>',body)
    for f in forms:
        print(' FORM action:',re.search(r'action="([^"]*)"',f))
        for inp in re.findall(r'<(?:input|textarea|select)[^>]*>',f): print('   ',inp[:160])
    # json?
    if body.strip().startswith('{'):
        print(' JSON:', body[:800])
    # visible hints
    for kw in ['master','key','import','ingest','url','fetch','internal','config','flag','admin','role']:
        for m in re.finditer(r'[^<>\n]{0,60}'+kw+r'[^<>\n]{0,80}', body, re.I):
            txt=m.group(0).strip()
            if txt and 'var(' not in txt and '{' not in txt: print('   hint:',txt[:140]); break
open('cn_sess.json','w').write(json.dumps(s.cookies.get_dict()))
