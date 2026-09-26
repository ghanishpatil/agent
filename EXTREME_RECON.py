#!/usr/bin/env python3
"""
EXTREME RECONNAISSANCE - Find ANY hint
"""

import requests
from bs4 import BeautifulSoup
import re
import base64

BASE_URL = "http://138.199.163.92:16969"

print("="*70)
print("EXTREME RECONNAISSANCE")
print("="*70)

# 1. Deep HTML analysis
print("\n[*] DEEP HTML ANALYSIS...")
resp = requests.get(f"{BASE_URL}/login")
html = resp.text

# Look for ANYTHING suspicious
patterns = [
    (r'<!--.*?-->', 'HTML Comments'),
    (r'password.*?["\']([^"\']+)["\']', 'Password patterns'),
    (r'user.*?["\']([^"\']+)["\']', 'User patterns'),
    (r'demo.*?["\']([^"\']+)["\']', 'Demo patterns'),
    (r'admin.*?["\']([^"\']+)["\']', 'Admin patterns'),
    (r'key.*?["\']([^"\']+)["\']', 'Key patterns'),
    (r'secret.*?["\']([^"\']+)["\']', 'Secret patterns'),
    (r'Kaal\{[^}]+\}', 'Flag patterns'),
    (r'[A-Za-z0-9+/]{20,}={0,2}', 'Base64 patterns'),
]

for pattern, name in patterns:
    matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
    if matches:
        print(f"\n  [{name}]")
        for match in matches[:5]:
            print(f"    {match[:100]}")

# 2. Check response headers for hints
print("\n[*] RESPONSE HEADERS...")
for key, value in resp.headers.items():
    print(f"  {key}: {value}")
    if 'password' in value.lower() or 'hint' in value.lower():
        print(f"    [!] SUSPICIOUS!")

# 3. Check cookies
print("\n[*] COOKIES...")
for cookie in resp.cookies:
    print(f"  {cookie.name} = {cookie.value}")

# 4. Try to decode any base64 in HTML
print("\n[*] DECODING BASE64 STRINGS...")
b64_matches = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', html)
for b64 in b64_matches[:10]:
    try:
        decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
        if decoded and len(decoded) > 3:
            print(f"  {b64[:30]}... -> {decoded[:50]}")
    except:
        pass

# 5. Check JavaScript for hints
print("\n[*] JAVASCRIPT ANALYSIS...")
soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')
for i, script in enumerate(scripts):
    if script.string:
        # Look for variable assignments
        vars = re.findall(r'(const|let|var)\s+(\w+)\s*=\s*["\']([^"\']+)["\']', script.string)
        if vars:
            print(f"\n  Script {i+1} variables:")
            for var in vars:
                print(f"    {var[1]} = {var[2][:50]}")

# 6. Check for hidden form fields
print("\n[*] HIDDEN FORM FIELDS...")
inputs = soup.find_all('input', type='hidden')
for inp in inputs:
    print(f"  {inp.get('name')} = {inp.get('value')}")

# 7. Try common credential files
print("\n[*] CHECKING CREDENTIAL FILES...")
cred_files = [
    '/credentials.txt', '/passwords.txt', '/users.txt',
    '/config.json', '/config.yml', '/.env',
    '/secrets.json', '/keys.txt',
]

for file in cred_files:
    r = requests.get(f"{BASE_URL}{file}")
    if r.status_code == 200:
        print(f"\n  [!!!] FOUND: {file}")
        print(f"       {r.text[:500]}")

# 8. Check for timing differences
print("\n[*] TIMING ANALYSIS...")
import time

usernames = ['demo', 'admin', 'nonexistent12345']
for username in usernames:
    data = {
        'pow_challenge': 'test',
        'pow_nonce': '0',
        'username': username,
        'password': 'wrongpassword'
    }
    
    start = time.time()
    resp = requests.post(f"{BASE_URL}/login", data=data)
    elapsed = time.time() - start
    
    print(f"  {username}: {elapsed:.4f}s (status: {resp.status_code})")

# 9. Check for version info
print("\n[*] VERSION INFORMATION...")
print(f"  Server: {resp.headers.get('Server', 'Unknown')}")

# Try to get more version info
for path in ['/version', '/api/version', '/.version', '/VERSION']:
    r = requests.get(f"{BASE_URL}{path}")
    if r.status_code == 200:
        print(f"  {path}: {r.text[:100]}")

print("\n[*] EXTREME RECON COMPLETE!")
