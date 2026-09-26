import requests, re, base64

BASE = 'https://ghostpanel-ctf.onrender.com'
s = requests.Session()

# Get FULL homepage raw
r = s.get(BASE, timeout=20)
print(r.text)
