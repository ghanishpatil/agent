#!/usr/bin/env python3
"""
Check if X-Secret changes or if there's a pattern
"""

import requests
import hashlib
import time

URL = "http://138.199.163.92:12871"

def get_secret():
    """Get X-Secret from a collision upload"""
    collision1_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89
55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70
"""
    
    file1 = bytes.fromhex(collision1_hex.replace('\n', ''))
    
    files = {'image': ('img.png', file1, 'image/png')}
    r = requests.post(f"{URL}/collision", files=files)
    
    return r.headers.get('X-Prefix'), r.headers.get('X-Secret'), r.text

# Check multiple times
print("[*] Checking X-Secret values across multiple requests...")
secrets = []

for i in range(5):
    prefix, secret, response = get_secret()
    secrets.append((prefix, secret, response))
    print(f"\n[{i+1}] Prefix: {prefix}")
    print(f"    Secret: {secret}")
    print(f"    Response: {response}")
    time.sleep(0.5)

# Check if they're all the same
unique_secrets = set(s[1] for s in secrets if s[1])
print(f"\n[*] Unique secrets found: {len(unique_secrets)}")

if len(unique_secrets) == 1:
    print(f"[+] Secret is constant: {list(unique_secrets)[0]}")
    print(f"\n[*] The flag is likely: Kaal{{{list(unique_secrets)[0]}}}")
else:
    print(f"[!] Secrets vary!")
    for s in unique_secrets:
        print(f"    - {s}")
