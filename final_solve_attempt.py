#!/usr/bin/env python3
"""
Final solve attempt - combine secret key with robots hint
"""

import requests
import time
from xml.etree import ElementTree as ET
import hashlib

TARGET_URL = "http://138.199.163.92:12669/"
SECRET_KEY = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"
ROBOTS_HINT = "q355q636678723p4"

print("="*60)
print("FINAL SOLVE ATTEMPT")
print("="*60)

# Wait to avoid rate limit
print("\n[*] Waiting 20 seconds...")
time.sleep(20)

# Try combining secret and robots hint
print("\n[*] Trying secret + robots hint...")
params = {
    'secret': SECRET_KEY,
    'q': ROBOTS_HINT
}

resp = requests.get(TARGET_URL + "svg.php", params=params)
print(f"  Status: {resp.status_code}, Length: {len(resp.text)}")

if resp.status_code == 200:
    # Check if response contains flag directly
    if 'Kaal{' in resp.text or 'kaal{' in resp.text.lower():
        print(f"\n{'='*60}")
        print(f"FLAG IN RESPONSE!")
        print(f"{'='*60}")
        import re
        flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
        if flag:
            print(flag.group(0))
            exit(0)
    
    # Parse and decode
    root = ET.fromstring(resp.text)
    rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
    
    bits = []
    for rect in rects:
        if rect.get('class') == 'bit':
            data_k = int(rect.get('data-k', 0))
            x = int(rect.get('x', 0))
            y = int(rect.get('y', 0))
            bits.append({'k': data_k, 'x': x, 'y': y})
    
    print(f"  Found {len(bits)} bits")
    
    # Try XOR with secret key
    print("\n[*] Trying XOR with secret key...")
    sorted_bits = sorted(bits, key=lambda b: (b['y'], b['x']))
    
    # Convert secret to bytes
    secret_bytes = SECRET_KEY.encode()
    
    result = []
    for i, b in enumerate(sorted_bits):
        key_byte = secret_bytes[i % len(secret_bytes)]
        decoded = b['k'] ^ key_byte
        if 32 <= decoded <= 126:
            result.append(chr(decoded))
        else:
            result.append('.')
    
    decoded_text = ''.join(result)
    print(f"  XOR result: {decoded_text[:200]}")
    
    if 'Kaal{' in decoded_text or 'kaal{' in decoded_text.lower():
        print(f"\n{'='*60}")
        print(f"FLAG FOUND!")
        print(f"{'='*60}")
        import re
        flag = re.search(r'Kaal\{[^}]+\}', decoded_text, re.IGNORECASE)
        if flag:
            print(flag.group(0))
            exit(0)

# Try using hash of secret as parameter
print("\n[*] Trying hash of secret...")
time.sleep(5)

secret_hash = hashlib.md5(SECRET_KEY.encode()).hexdigest()
print(f"  MD5: {secret_hash}")

resp = requests.get(TARGET_URL + "svg.php", params={'secret': secret_hash})
print(f"  Status: {resp.status_code}, Length: {len(resp.text)}")

if 'Kaal{' in resp.text or 'kaal{' in resp.text.lower():
    print(f"\n{'='*60}")
    print(f"FLAG FOUND!")
    print(f"{'='*60}")
    import re
    flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
    if flag:
        print(flag.group(0))
        exit(0)

# Try other endpoints with secret
print("\n[*] Trying other endpoints with secret...")
time.sleep(5)

for endpoint in ['/', '/flag', '/lore']:
    resp = requests.get(TARGET_URL.rstrip('/') + endpoint, params={'secret': SECRET_KEY})
    print(f"\n  {endpoint}: {resp.status_code}")
    if 'Kaal{' in resp.text or 'kaal{' in resp.text.lower():
        print(f"  [!] FLAG FOUND!")
        import re
        flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
        if flag:
            print(f"  {flag.group(0)}")
            exit(0)

print("\n" + "="*60)
print("No flag found yet. The SVG might need multiple requests or specific timing.")
print("="*60)
