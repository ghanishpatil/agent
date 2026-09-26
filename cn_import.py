import requests, re, random, string, base64, json
BASE='http://15.252.91.100'
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
def csrf(h): 
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"',h); return m.group(1) if m else None
def solve(h):
    q=re.search(r'class="captcha-question"[^>]*>(.*?)</',h,re.S); cid=re.search(r'name="captcha_id" value="([^"]*)"',h)
    m=re.search(r'(\d+)\s*([\+\-\*x×])\s*(\d+)',q.group(1)); a,op,b=int(m.group(1)),m.group(2),int(m.group(3))
    return cid.group(1),{'+':a+b,'-':a-b,'*':a*b}[op]
U='dfr'+''.join(random.choices(string.ascii_lowercase,k=7)); P='Passw0rd!zz'
r=s.get(BASE+'/register/'); t=csrf(r.text); cid,ans=solve(r.text)
s.post(BASE+'/register/',data={'csrfmiddlewaretoken':t,'username':U,'email':U+'@c.com','password':P,'captcha_id':cid,'captcha_answer':str(ans)},headers={'Referer':BASE+'/register/'})
open('cn_cookies.json','w').write(json.dumps(s.cookies.get_dict()))
print('user',U,'cookies saved')

r=s.get(BASE+'/import/config/')
# print full visible body (strip style block)
body=r.text
body=re.sub(r'<style[\s\S]*?</style>','',body)
body=re.sub(r'<[^>]+>',' ',body)
body=re.sub(r'\s+\n','\n',body)
body=re.sub(r'[ \t]+',' ',body)
print(body[:4000])
