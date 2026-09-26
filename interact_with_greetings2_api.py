#!/usr/bin/env python3
"""Interact with the Greetings 2 API"""

import requests
import json

URL = "http://138.199.163.92:13696/api"

print("=" * 60)
print("GREETINGS 2 API INTERACTION")
print("=" * 60)

# Try basic GET request
print("\n[*] Trying GET request...")
try:
    r = requests.get(URL, timeout=5)
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.text[:500]}")
except Exception as e:
    print(f"    Error: {e}")

# Try POST with name
print("\n[*] Trying POST with name...")
try:
    data = {"name": "warrior"}
    r = requests.post(URL, json=data, timeout=5)
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.text[:500]}")
except Exception as e:
    print(f"    Error: {e}")

# Try with pickle/hex payload (from bytecode analysis)
print("\n[*] Trying with obj parameter...")
try:
    data = {"obj": "test"}
    r = requests.post(URL, json=data, timeout=5)
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.text[:500]}")
except Exception as e:
    print(f"    Error: {e}")

# Try different endpoints
print("\n[*] Trying /flag endpoint...")
try:
    r = requests.get(URL.replace('/api', '/flag'), timeout=5)
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.text[:500]}")
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "=" * 60)
