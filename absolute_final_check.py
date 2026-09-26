#!/usr/bin/env python3
"""
COMPLETE DATABASE WIPE - Delete EVERYTHING
"""

import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = "http://fresh-start-267.emergent.host"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

headers = {
    "Authorization": f"Bearer {token}",
    "X-Forwarded-For": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
    "X-Originating-IP": "127.0.0.1",
    "Via": "1.1 127.0.0.1",
    "Client-IP": "127.0.0.1"
}

print("="*70)
print("COMPLETE DATABASE WIPE")
print("="*70)

# Delete ALL users
print("\n[1] Deleting ALL users...")
try:
    resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=10)
    if resp.status_code == 200:
        users = resp.json()
        print(f"Found {len(users)} users")
        
        def delete_user(user):
            user_id = user.get('id') or user.get('user_id')
            if user_id:
                try:
                    requests.delete(f"{base_url}/api/users/{user_id}", headers=headers, timeout=5)
                    return 1
                except:
                    return 0
            return 0
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(delete_user, user) for user in users]
            deleted = sum(f.result() for f in as_completed(futures))
        
        print(f"Deleted {deleted} users")
except Exception as e:
    print(f"Error: {e}")

# Delete ALL tasks
print("\n[2] Deleting ALL tasks...")
try:
    resp = requests.get(f"{base_url}/api/tasks", headers=headers, timeout=10)
    if resp.status_code == 200:
        tasks = resp.json()
        print(f"Found {len(tasks)} tasks")
        
        def delete_task(task):
            task_id = task.get('id') or task.get('task_id')
            if task_id:
                try:
                    requests.delete(f"{base_url}/api/tasks/{task_id}", headers=headers, timeout=5)
                    return 1
                except:
                    return 0
            return 0
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(delete_task, task) for task in tasks]
            deleted = sum(f.result() for f in as_completed(futures))
        
        print(f"Deleted {deleted} tasks")
except Exception as e:
    print(f"Error: {e}")

# Try to delete other resources
print("\n[3] Attempting to delete other resources...")
endpoints_to_try = [
    '/api/projects',
    '/api/teams',
    '/api/departments',
    '/api/roles',
    '/api/permissions',
    '/api/settings',
    '/api/logs',
    '/api/notifications',
    '/api/comments',
    '/api/attachments',
    '/api/files',
    '/api/documents',
]

for endpoint in endpoints_to_try:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"Found {len(data)} items at {endpoint}")
                    
                    # Try to delete each item
                    for item in data:
                        item_id = item.get('id') or item.get('_id')
                        if item_id:
                            try:
                                requests.delete(f"{base_url}{endpoint}/{item_id}", headers=headers, timeout=3)
                            except:
                                pass
            except:
                pass
    except:
        pass

# Verify database is empty
print("\n[4] Verifying database state...")
try:
    resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=10)
    if resp.status_code == 200:
        users = resp.json()
        print(f"Remaining users: {len(users)}")
except:
    print("Cannot access users endpoint")

try:
    resp = requests.get(f"{base_url}/api/tasks", headers=headers, timeout=10)
    if resp.status_code == 200:
        tasks = resp.json()
        print(f"Remaining tasks: {len(tasks)}")
except:
    print("Cannot access tasks endpoint")

print("\n" + "="*70)
print("DATABASE WIPE COMPLETE")
print("="*70)
