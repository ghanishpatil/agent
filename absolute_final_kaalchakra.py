#!/usr/bin/env python3
"""
Absolute final attempt - decode X-Secret properly
"""

import requests
import re
import hashlib

TARGET_URL = "http://138.199.163.92:12871/"

# The X-Secret we got from the headers
secret = "38h4vg6s45ch1lr19x4pe18s55r2kh1lx5331mh1mc5656w0"
prefix = "laak_560c83ed"

print("="*60)
print("FINAL KAALCHAKRA DECODE")
print("="*60)

# The secret is 48 characters - same length as a typical flag
# Let me try EVERY decoding method

# Method 1: The secret might BE the flag with Kaal{} wrapper
flag1 = f"Kaal{{{secret}}}"
print(f"\n1. Direct wrap: {flag1}")

# Method 2: Reverse it
flag2 = f"Kaal{{{secret[::-1]}}}"
print(f"2. Reversed: {flag2}")

# Method 3: Use only letters
letters = ''.join(c for c in secret if c.isalpha())
flag3 = f"Kaal{{{letters}}}"
print(f"3. Letters only: {flag3}")

# Method 4: Use only numbers
numbers = ''.join(c for c in secret if c.isdigit())
flag4 = f"Kaal{{{numbers}}}"
print(f"4. Numbers only: {flag4}")

# Method 5: Alternate chars
alt1 = ''.join(secret[i] for i in range(0, len(secret), 2))
flag5 = f"Kaal{{{alt1}}}"
print(f"5. Every 2nd char: {flag5}")

# Method 6: The prefix might be part of it
flag6 = f"Kaal{{{prefix}_{secret[:20]}}}"
print(f"6. With prefix: {flag6}")

# Method 7: MD5 of secret
md5_secret = hashlib.md5(secret.encode()).hexdigest()
flag7 = f"Kaal{{{md5_secret}}}"
print(f"7. MD5 of secret: {flag7}")

# Method 8: Try submitting to server to see if it gives us the flag
print("\n" + "="*60)
print("Testing with server")
print("="*60)

session = requests.Session()

# Upload collision files again and check ALL responses carefully
with open('coll_a.bin', 'rb') as f:
    resp1 = session.post(TARGET_URL + 'collision', files={'image': f})

print(f"\nResponse 1: {resp1.text}")
print(f"Headers: {dict(resp1.headers)}")

# Check if there's a flag in the response
if 'kaal{' in resp1.text.lower():
    flag = re.search(r'Kaal\{[^}]+\}', resp1.text, re.IGNORECASE)
    if flag:
        print(f"\n{'='*60}")
        print(f"FLAG FOUND: {flag.group(0)}")
        print(f"{'='*60}")
        exit(0)

# Upload second file
with open('coll_b.bin', 'rb') as f:
    resp2 = session.post(TARGET_URL + 'collision', files={'image': f})

print(f"\nResponse 2: {resp2.text}")
print(f"Headers: {dict(resp2.headers)}")

if 'kaal{' in resp2.text.lower():
    flag = re.search(r'Kaal\{[^}]+\}', resp2.text, re.IGNORECASE)
    if flag:
        print(f"\n{'='*60}")
        print(f"FLAG FOUND: {flag.group(0)}")
        print(f"{'='*60}")
        exit(0)

# Check if the X-Secret changed
new_secret = resp2.headers.get('X-Secret', '')
if new_secret and new_secret != secret:
    print(f"\n[!] X-Secret changed to: {new_secret}")
    print(f"This might be the flag: Kaal{{{new_secret}}}")

# Try accessing other endpoints with the session
endpoints = ['/', '/flag', '/success', '/win', '/collision']
for endpoint in endpoints:
    try:
        resp = session.get(TARGET_URL.rstrip('/') + endpoint)
        if 'kaal{' in resp.text.lower():
            flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
            if flag:
                print(f"\n{'='*60}")
                print(f"FLAG at {endpoint}: {flag.group(0)}")
                print(f"{'='*60}")
                exit(0)
    except:
        pass

print("\n" + "="*60)
print("MOST LIKELY FLAGS TO TRY:")
print("="*60)
print(f"1. Kaal{{{secret}}}")
print(f"2. Kaal{{{letters}}}")
print(f"3. Kaal{{HAUNTED_PUMPKIN}}")
print(f"4. Kaal{{PUMPKIN}}")
print("="*60)
