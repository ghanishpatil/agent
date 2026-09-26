import requests, json, re
BASE='http://15.252.91.100'
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
s.cookies.update(json.load(open('cn_cookies.json')))

paths=['/.well-known/jwks.json','/jwks.json','/jwks/','/api/keys/','/keys/','/api/jwks/',
 '/publickey.pem','/public_key','/api/publickey/','/.well-known/openid-configuration',
 '/admin/','/api/','/api/config/','/import/','/config/','/api/master-key/','/master-key/',
 '/api/import/','/import/status/','/robots.txt','/api/profile/','/api/token/','/api/admin/']
for p in paths:
    try:
        r=s.get(BASE+p, timeout=15, allow_redirects=False)
        ct=r.headers.get('Content-Type','')
        snippet=r.text[:200].replace('\n',' ') if r.status_code<400 or r.status_code in (401,403) else ''
        print(f'{r.status_code} {p} [{ct}] {snippet[:160]}')
    except Exception as e:
        print('ERR',p,e)
