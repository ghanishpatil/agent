import requests, re, random, string, base64, json
BASE='http://15.252.91.100'
def csrf(h): 
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"',h); return m.group(1) if m else None
def solve(h):
    q=re.search(r'class="captcha-question"[^>]*>(.*?)</',h,re.S); cid=re.search(r'name="captcha_id" value="([^"]*)"',h)
    m=re.search(r'(\d+)\s*([\+\-\*x×])\s*(\d+)',q.group(1)); a,op,b=int(m.group(1)),m.group(2),int(m.group(3))
    return cid.group(1),{'+':a+b,'-':a-b,'*':a*b}[op]

def reg():
    s=requests.Session(); s.headers.update({'User-Agent':'M'})
    U='dfr'+''.join(random.choices(string.ascii_lowercase,k=8)); P='Passw0rd!zz'
    r=s.get(BASE+'/register/'); t=csrf(r.text); cid,ans=solve(r.text)
    s.post(BASE+'/register/',data={'csrfmiddlewaretoken':t,'username':U,'email':U+'@c.com','password':P,'captcha_id':cid,'captcha_answer':str(ans)},headers={'Referer':BASE+'/register/'})
    return s.cookies.get('cloudnine_access')

toks=[]
for i in range(4):
    tk=reg()
    if tk: toks.append(tk); print('tok',i,'len sig', len(tk.split('.')[2]))
json.dump(toks, open('cn_tokens.json','w'))
# sig byte length
def b64d(x): return base64.urlsafe_b64decode(x+'='*(-len(x)%4))
for t in toks[:1]:
    print('sig bytes', len(b64d(t.split('.')[2])))
print('collected', len(toks))
