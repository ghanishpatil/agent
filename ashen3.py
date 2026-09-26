import requests, re, json, hashlib

BASE = 'https://ashen-checkpoint-challenge--yoriichi13.replit.app'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})

# Get challenge
print('=== /api/chakra/challenge ===')
r = s.get(BASE + '/api/chakra/challenge', timeout=20)
print(r.status_code, r.headers.get('Content-Type',''))
print(r.text[:3000])

print('\n=== /api/chakra/status ===')
r2 = s.get(BASE + '/api/chakra/status', timeout=15)
print(r2.status_code)
print(r2.text[:1000])
