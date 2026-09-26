#!/usr/bin/env python3
"""
Force delete ALL users including deactivated ones
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

print("FORCE DELETING ALL USERS INCLUDING DEACTIVATED")

# Get all users
resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=10)
users = resp.json()
print(f"Found {len(users)} users (including deactivated)")

def force_delete(user):
    user_id = user.get('id')
    email = user.get('email')
    is_active = user.get('is_active')
    
    if user_id:
        try:
            # Try DELETE
            del_resp = requests.delete(f"{base_url}/api/users/{user_id}", headers=headers, timeout=5)
            
            # Try PUT to permanently delete
            requests.put(f"{base_url}/api/users/{user_id}/delete", headers=headers, timeout=5)
            
            # Try POST to remove
            requests.post(f"{base_url}/api/users/{user_id}/remove", headers=headers, timeout=5)
            
            return f"Deleted {email} (active={is_active})"
        except:
            return None
    return None

with ThreadPoolExecutor(max_workers=30) as executor:
    futures = [executor.submit(force_delete, user) for user in users]
    
    for future in as_completed(futures):
        result = future.result()
        if result:
            print(result)

# Verify
print("\nVerifying...")
resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=10)
remaining = resp.json()
print(f"Remaining users: {len(remaining)}")
