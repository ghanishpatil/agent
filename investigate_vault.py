#!/usr/bin/env python3
"""
Investigate /vault endpoint
"""

import requests

BASE_URL = "http://138.199.163.92:16969"

print("="*60)
print("INVESTIGATING /vault")
print("="*60)

# Check /vault
resp = requests.get(f"{BASE_URL}/vault", allow_redirects=False)
print(f"\n[*] /vault (no redirect):")
print(f"  Status: {resp.status_code}")
print(f"  Headers: {dict(resp.headers)}")
print(f"  Content: {resp.text}")

# Follow redirect
resp_follow = requests.get(f"{BASE_URL}/vault", allow_redirects=True)
print(f"\n[*] /vault (with redirect):")
print(f"  Final URL: {resp_follow.url}")
print(f"  Status: {resp_follow.status_code}")
print(f"  Content preview: {resp_follow.text[:500]}")

# Try /vault with different methods
print("\n[*] Trying different HTTP methods on /vault...")
for method in ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD']:
    try:
        r = requests.request(method, f"{BASE_URL}/vault", timeout=3, allow_redirects=False)
        if r.status_code not in [404, 405]:
            print(f"  {method}: {r.status_code}")
    except:
        pass

# Try /vault with parameters
print("\n[*] Trying /vault with parameters...")
params_list = [
    {'id': '1'},
    {'document': '1'},
    {'file': '1'},
    {'q': 'flag'},
    {'search': 'flag'},
]

for params in params_list:
    r = requests.get(f"{BASE_URL}/vault", params=params, allow_redirects=False)
    if r.status_code != 302:
        print(f"  With {params}: {r.status_code}")
        print(f"    {r.text[:200]}")

# Try /vault subpaths
print("\n[*] Trying /vault subpaths...")
subpaths = [
    '/vault/1',
    '/vault/2',
    '/vault/documents',
    '/vault/files',
    '/vault/list',
    '/vault/search',
    '/vault/admin',
]

for path in subpaths:
    r = requests.get(f"{BASE_URL}{path}", allow_redirects=False)
    if r.status_code not in [404, 405]:
        print(f"  {path}: {r.status_code}")
        if len(r.text) < 300:
            print(f"    {r.text}")

print("\n[*] Investigation complete!")
