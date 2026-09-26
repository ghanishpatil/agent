import requests, re
BASE='http://15.252.91.100'
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
r=s.get(BASE+'/register/')
# find the div class="captcha-question" occurrences in body
for m in re.finditer(r'class="captcha-question"[^>]*>(.*?)</', r.text, re.S):
    print('Q:', repr(m.group(1)))
# broader: any element containing 'What is'
for m in re.finditer(r'(What is[^<]*)', r.text):
    print('WHATIS:', repr(m.group(1)))
