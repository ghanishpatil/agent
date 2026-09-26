import requests, re, sys
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://15.252.91.100'
s=requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0'})
r=s.get(BASE+'/register/', timeout=20)
# extract everything inside <form>...</form>
forms=re.findall(r'<form[\s\S]*?</form>', r.text)
for f in forms:
    # strip to inputs/labels/text
    fields=re.findall(r'<(input|textarea|select|label|button)[^>]*>', f)
    print('--- FORM action:', re.search(r'action="([^"]*)"',f))
    for line in re.findall(r'<(?:input|textarea|select)[^>]*>', f):
        print('  ', line)
    # captcha question text
    q=re.findall(r'captcha-question[^>]*>([^<]*)<', f)
    print('  CAPTCHA Q:', q)
    help=re.findall(r'form-help[^>]*>([\s\S]*?)</', f)
    print('  HELP:', [h.strip() for h in help])
# also print any visible text hints
csrf=re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"', r.text)
print('csrf:', csrf.group(1) if csrf else None)
print('cookies:', s.cookies.get_dict())
