#!/usr/bin/env python3
"""
Check all possible endpoints and methods
"""

import requests

URL = "http://138.199.163.92:12871"

# Common endpoints
endpoints = [
    '/', '/flag', '/collision', '/verify', '/check', '/success', '/win',
    '/admin', '/api', '/secret', '/kaal', '/laak', '/time', '/traveler',
    '/md5', '/hash', '/puppy', '/image', '/bonus', '/scroll', '/lock',
    '/echo', '/magic', '/de43e58e', '/38h4vg6s45ch1lr19x4pe18s55r2kh1lx5331mh1mc5656w0'
]

print("[*] Checking GET endpoints...")
for endpoint in endpoints:
    try:
        r = requests.get(f"{URL}{endpoint}", timeout=2)
        if r.status_code == 200 and 'Kaal{' in r.text:
            print(f"[!] FLAG at GET {endpoint}: {r.text}")
            break
        elif r.status_code == 200 and endpoint not in ['/', '/image.png']:
            print(f"[+] GET {endpoint}: {r.status_code} - {r.text[:100]}")
    except:
        pass

print("\n[*] Checking POST endpoints...")
for endpoint in endpoints:
    try:
        r = requests.post(f"{URL}{endpoint}", timeout=2)
        if r.status_code == 200 and 'Kaal{' in r.text:
            print(f"[!] FLAG at POST {endpoint}: {r.text}")
            break
        elif r.status_code not in [404, 500]:
            print(f"[+] POST {endpoint}: {r.status_code} - {r.text[:100]}")
    except:
        pass
