#!/usr/bin/env python3
"""
Check main pages with secret
"""

import requests
import time

TARGET_URL = "http://138.199.163.92:12669/"
SECRET_KEY = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

print("="*60)
print("CHECKING PAGES WITH SECRET")
print("="*60)

time.sleep(20)

# Check main page
print("\n[*] Checking main page with secret...")
resp = requests.get(TARGET_URL, params={'secret': SECRET_KEY})
print(f"  Status: {resp.status_code}")
print(f"  Content:\n{resp.text}")

if 'Kaal{' in resp.text or 'kaal{' in resp.text.lower():
    print(f"\n{'='*60}")
    print(f"FLAG FOUND!")
    print(f"{'='*60}")
    import re
    flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
    if flag:
        print(flag.group(0))

time.sleep(5)

# Check lore page
print("\n[*] Checking lore page with secret...")
resp = requests.get(TARGET_URL + "lore", params={'secret': SECRET_KEY})
print(f"  Status: {resp.status_code}")
print(f"  Content:\n{resp.text}")

if 'Kaal{' in resp.text or 'kaal{' in resp.text.lower():
    print(f"\n{'='*60}")
    print(f"FLAG FOUND!")
    print(f"{'='*60}")
    import re
    flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
    if flag:
        print(flag.group(0))

print("\n" + "="*60)
