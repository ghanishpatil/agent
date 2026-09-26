import requests, re, sys, random, string
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://15.252.91.100'
s=requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0'})

def csrf(html):
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"', html)
    return m.group(1) if m else None

def solve_captcha(html):
    q=re.search(r'class="captcha-question"[^>]*>(.*?)</', html, re.S)
    cid=re.search(r'name="captcha_id" value="([^"]*)"', html)
    if not q: return None,None,None
    text=q.group(1).strip()
    m=re.search(r'(\d+)\s*([\+\-\*x×])\s*(\d+)', text)
    ans=None
    if m:
        a,op,b=int(m.group(1)),m.group(2),int(m.group(3))
        ans={'+':a+b,'-':a-b,'*':a*b,'x':a*b,'×':a*b}[op]
    return text, (cid.group(1) if cid else None), ans

USER='dfr'+''.join(random.choices(string.ascii_lowercase+string.digits,k=6))
PW='Passw0rd!'+''.join(random.choices(string.ascii_lowercase,k=4))
print('creds', USER, PW)

r=s.get(BASE+'/register/')
tok=csrf(r.text); text,cid,ans=solve_captcha(r.text)
print('captcha',text,'=',ans,'id',cid)
data={'csrfmiddlewaretoken':tok,'username':USER,'email':USER+'@corp.com','password':PW,'captcha_id':cid,'captcha_answer':str(ans)}
r=s.post(BASE+'/register/', data=data, headers={'Referer':BASE+'/register/'}, allow_redirects=True)
print('register ->', r.status_code, r.url)
errs=re.findall(r'field-error[^>]*>([\s\S]*?)</', r.text)+re.findall(r'alert[^>]*>([\s\S]*?)</',r.text)
print('msgs:', [e.strip() for e in errs if e.strip()][:6])

# login if needed
if '/login' in r.url or 'login' in r.url:
    r=s.get(BASE+'/login/'); tok=csrf(r.text)
    text,cid,ans=solve_captcha(r.text)
    d={'csrfmiddlewaretoken':tok,'username':USER,'password':PW}
    if cid: d.update({'captcha_id':cid,'captcha_answer':str(ans)})
    r=s.post(BASE+'/login/', data=d, headers={'Referer':BASE+'/login/'}, allow_redirects=True)
    print('login ->', r.status_code, r.url)

# save creds and cookies
open('cn_session.txt','w').write(f'{USER}\n{PW}\n{s.cookies.get_dict()}\n')
print('cookies', s.cookies.get_dict())
# fetch dashboard/home after auth
r=s.get(BASE+'/')
print('=== post-auth home ===', r.status_code, r.url)
# print links
links=set(re.findall(r'href="(/[^"]*)"', r.text))
print('LINKS:', sorted(links))
open('cn_home.html','w',encoding='utf-8').write(r.text)
