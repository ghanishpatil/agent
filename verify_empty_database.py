#!/usr/bin/env python3
"""
Verify database is completely empty and check all endpoints
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

print("="*70)
print("DATABASE VERIFICATION")
print("="*70)

# Check users
print("\n[1] Checking /api/users...")
try:
    resp = requests.get(f"{base_url}/api/users", headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Users count: {len(data)}")
        if len(data) > 0:
            print(f"Sample: {json.dumps(data[:3], indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Check tasks
print("\n[2] Checking /api/tasks...")
try:
    resp = requests.get(f"{base_url}/api/tasks", headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Tasks count: {len(data)}")
        if len(data) > 0:
            print(f"Sample: {json.dumps(data[:3], indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Check admin panel
print("\n[3] Checking /api/admin...")
try:
    resp = requests.get(f"{base_url}/api/admin", headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Check stats
print("\n[4] Checking /api/admin/stats...")
try:
    resp = requests.get(f"{base_url}/api/admin/stats", headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Check dashboard
print("\n[5] Checking /api/admin/dashboard...")
try:
    resp = requests.get(f"{base_url}/api/admin/dashboard", headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70)
