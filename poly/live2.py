import requests
base="https://polynomial.secso.cc"
s=requests.Session()
r=s.get(base+"/",timeout=20)
print("GET / headers:")
for k,v in r.headers.items(): print("  ",k,":",v)
print("cookies:", s.cookies.get_dict())
print("="*60)
# report flow: does it return a token / status url?
r2=s.post(base+"/report",data={"url":"/?format=standard&autoEval=1"},timeout=20,allow_redirects=False)
print("POST /report:",r2.status_code)
for k,v in r2.headers.items(): print("  ",k,":",v)
print("body:",repr(r2.text[:300]))
print("cookies after report:", s.cookies.get_dict())
print("="*60)
# probe potential flag/status endpoints
for p in ["/flag","/status","/admin","/bot","/report/status","/api","/config","/instance","/health","/whoami"]:
    try:
        rr=s.get(base+p,timeout=12,allow_redirects=False)
        print("GET",p,"->",rr.status_code,rr.headers.get("content-type"),"len",len(rr.text))
    except Exception as e:
        print("GET",p,"ERR",e)
