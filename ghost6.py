import requests, re, base64

BASE = 'https://ghostpanel-ctf.onrender.com'
s = requests.Session()

# Check legacy-login full source
r = s.get(BASE + '/legacy-login', timeout=15)
print('=== LEGACY LOGIN FULL ===')
print(r.text)
