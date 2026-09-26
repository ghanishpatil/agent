#!/usr/bin/env python3
import requests
import re

TARGET_URL = "http://138.199.163.92:12871/"

session = requests.Session()

# Upload B first
print("[*] Uploading B first...")
with open('coll_b.bin', 'rb') as f:
    resp1 = session.post(TARGET_URL + 'collision', files={'image': f})
print(f"[+] Response 1: {resp1.text}")

# Then upload A
print("\n[*] Uploading A second...")
with open('coll_a.bin', 'rb') as f:
    resp2 = session.post(TARGET_URL + 'collision', files={'image': f})
print(f"[+] Response 2: {resp2.text}")

# Check for flag
for resp in [resp1, resp2]:
    if 'kaal{' in resp.text.lower():
        flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
        if flag:
            print(f"\n[!!!] FLAG: {flag.group(0)}")
