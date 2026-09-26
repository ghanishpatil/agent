import requests, re

BASE = 'https://enchanting-naiad-0167f9.netlify.app'
s = requests.Session()

for js in ['js/app.js', 'js/audio.js']:
    r = s.get(BASE + '/' + js, timeout=10)
    print(f'=== {js} ===')
    flags = re.findall(r'CHAKRA\{[^}]+\}', r.text)
    print('FLAGS:', flags)
    print(r.text[:2000])
    print()
