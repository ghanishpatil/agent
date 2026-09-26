#!/usr/bin/env python3
import requests
import re
import time

TARGET_URL = "http://138.199.163.92:12871/"

# Create fresh session
session = requests.Session()

# Upload A
print("[*] Fresh session - Uploading A...")
with open('coll_a.bin', 'rb') as f:
    resp1 = session.post(TARGET_URL + 'collision', files={'image': f})
print(f"[+] Response 1: {resp1.text}")

time.sleep(0.5)

# Upload B
print("\n[*] Uploading B...")
with open('coll_b.bin', 'rb') as f:
    resp2 = session.post(TARGET_URL + 'collision', files={'image': f})
print(f"[+] Response 2: {resp2.text}")

# Check responses
for i, resp in enumerate([resp1, resp2], 1):
    if 'kaal{' in resp.text.lower():
        flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
        if flag:
            print(f"\n[!!!] FLAG IN RESPONSE {i}: {flag.group(0)}")
    
    # Also check if there's a redirect or additional info
    print(f"\nResponse {i} headers: {dict(resp.headers)}")
    print(f"Response {i} cookies: {dict(resp.cookies)}")
