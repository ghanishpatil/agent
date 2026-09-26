import requests, re

BASE = 'https://ghostpanel-ctf.onrender.com'
s = requests.Session()

# Test SSTI - check if 7*7=49 appears in response
r = s.post(BASE + '/legacy-login', data={'username': '{{7*7}}', 'password': 'x'}, timeout=12)
print('7*7 response:')
print(r.text)
print()

# Also try password field
r2 = s.post(BASE + '/legacy-login', data={'username': 'admin', 'password': '{{7*7}}'}, timeout=12)
print('password 7*7:')
print(r2.text)
