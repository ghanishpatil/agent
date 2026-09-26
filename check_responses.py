#!/usr/bin/env python3
"""
Check what the 169-byte responses contain
"""

import requests

TARGET_URL = "http://138.199.163.92:12669/"
hint = "q355q636678723p4"

print("="*60)
print("CHECKING RESPONSES")
print("="*60)

# Check with secret parameter
print("\n[*] Response with secret parameter:")
resp = requests.get(TARGET_URL + "svg.php", params={'secret': hint})
print(resp.text)
print(f"\nHeaders: {dict(resp.headers)}")

# Check with k parameter
print("\n[*] Response with k=355:")
resp = requests.get(TARGET_URL + "svg.php", params={'k': '355'})
print(resp.text)

# Try the hint broken down
print("\n[*] Trying q=355, q=636, p=4...")
resp = requests.get(TARGET_URL + "svg.php", params={'q': '355'})
print(f"q=355: {resp.text}")

resp = requests.get(TARGET_URL + "svg.php", params={'q': '636'})
print(f"\nq=636: {resp.text}")

resp = requests.get(TARGET_URL + "svg.php", params={'p': '4'})
print(f"\np=4: {resp.text}")

# Try combined
resp = requests.get(TARGET_URL + "svg.php", params={'q': '355', 'p': '4'})
print(f"\nq=355&p=4: {resp.text}")

print("\n" + "="*60)
