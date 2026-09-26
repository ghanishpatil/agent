import requests, re, json

BASE = 'https://ashen-checkpoint-challenge--yoriichi13.replit.app'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

# Get JS file
r = s.get(BASE + '/assets/index-qJ7ul-BS.js', timeout=30)
js = r.text
print('JS size:', len(js))

# Find API endpoints
endpoints = list(set(re.findall(r'["\`](/api/[^"\'`\s\)]{2,60})', js)))
print('API endpoints:', endpoints)

# Find fetch calls
fetches = list(set(re.findall(r'fetch\(["\'`]([^"\'`]+)["\'`]', js)))
print('Fetch URLs:', fetches)

# print 2000 chars around 'api' occurrences
idxs = [m.start() for m in re.finditer(r'/api/', js)]
for i in idxs[:5]:
    print(f'\n[api@{i}]:', js[max(0,i-50):i+150])
