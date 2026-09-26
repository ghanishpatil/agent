import requests, re
BASE='http://15.252.91.100'
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
r=s.get(BASE+'/register/')
i=r.text.find('captcha')
print(repr(r.text[i-200:i+600]))
