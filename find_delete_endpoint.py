#!/usr/bin/env python3
"""
Find the correct database deletion endpoint
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

print("="*60)
print("FINDING CORRECT ENDPOINTS")
print("="*60)

# Test all HTTP methods on various endpoints
endpoints_to_test = [
    '/api/admin',
    '/api/admin/',
    '/api/tasks',
    '/api/users',
    '/api/admin/tasks',
    '/api/admin/users',
    '/api/admin/delete',
    '/api/admin/reset',
    '/api/admin/clear',
    '/api/admin/wipe',
    '/api/delete',
    '/api/reset',
]

methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']

for endpoint in endpoints_to_test:
    url = base_url + endpoint
    print(f"\n[*] Testing {endpoint}:")
    
    for method in methods:
        try:
            if method == 'GET':
                resp = requests.get(url, headers=headers, timeout=3)
            elif method == 'POST':
                resp = requests.post(url, headers=headers, json={}, timeout=3)
            elif method == 'PUT':
                resp = requests.put(url, headers=headers, json={}, timeout=3)
            elif method == 'DELETE':
                resp = requests.delete(url, headers=headers, timeout=3)
            elif method == 'PATCH':
                resp = requests.patch(url, headers=headers, json={}, timeout=3)
            elif method == 'OPTIONS':
                resp = requests.options(url, headers=headers, timeout=3)
            
            if resp.status_code != 404:
                print(f"  {method}: {resp.status_code}")
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        print(f"    Response: {json.dumps(data, indent=2)[:200]}")
                    except:
                        print(f"    Response: {resp.text[:200]}")
                        
        except Exception as e:
            pass

# Try to get all tasks and delete them
print("\n" + "="*60)
print("TRYING TO DELETE ALL TASKS")
print("="*60)

try:
    # Get all tasks
    resp = requests.get(f"{base_url}/api/tasks", headers=headers, timeout=5)
    print(f"\nGET /api/tasks: {resp.status_code}")
    
    if resp.status_code == 200:
        tasks = resp.json()
        print(f"Found {len(tasks)} tasks")
        print(json.dumps(tasks, indent=2)[:500])
        
        # Try to delete each task
        for task in tasks:
            task_id = task.get('id') or task.get('task_id')
            if task_id:
                print(f"\n[*] Deleting task {task_id}...")
                del_resp = requests.delete(f"{base_url}/api/tasks/{task_id}", headers=headers, timeout=5)
                print(f"Status: {del_resp.status_code}")
                print(f"Response: {del_resp.text[:200]}")
                
except Exception as e:
    print(f"Error: {e}")

# Try to delete all users
print("\n" + "="*60)
print("TRYING TO DELETE ALL USERS")
print("="*60)

try:
    # Get all users
    resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=5)
    print(f"\nGET /api/users: {resp.status_code}")
    
    if resp.status_code == 200:
        users = resp.json()
        print(f"Found {len(users)} users")
        print(json.dumps(users, indent=2)[:500])
        
        # Try to delete each user (except admin)
        for user in users:
            user_id = user.get('id') or user.get('user_id')
            email = user.get('email')
            
            if user_id and email != "admin@ethara.ai":
                print(f"\n[*] Deleting user {user_id} ({email})...")
                del_resp = requests.delete(f"{base_url}/api/users/{user_id}", headers=headers, timeout=5)
                print(f"Status: {del_resp.status_code}")
                print(f"Response: {del_resp.text[:200]}")
                
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("COMPLETE")
print("="*60)
