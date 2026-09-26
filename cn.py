import requests, re, sys
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://15.252.91.100'
s=requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0'})

def get(p):
    r=s.get(BASE+p, timeout=20)
    return r
def show(r, n=4000):
    print('URL',r.url,'STATUS',r.status_code,'LEN',len(r.text))
    print(r.text[:n])

r=get('/register/')
print('=== /register/ ===')
show(r, 6000)
