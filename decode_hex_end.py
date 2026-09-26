#!/usr/bin/env python3
"""
Decode the hex data at the end of the file
"""

import binascii
import base64
import re

# The hex from the end
hex_data = "0a4b45595f5f5f5f5f5f5f5f5f5f5f5f3a56314a50546b644c52566b3d0a0a4b61616c7b315f7468316e6b5f746831355f31355f7772306e677d0a"

decoded = binascii.unhexlify(hex_data)
print(f"[*] Decoded hex:")
print(decoded)
print(f"\n[*] As string:")
print(decoded.decode('utf-8', errors='ignore'))

# Parse it
lines = decoded.decode('utf-8', errors='ignore').split('\n')
for line in lines:
    print(f"\nLine: {line}")
    
    if ':' in line:
        parts = line.split(':')
        key_name = parts[0].strip()
        key_value = parts[1].strip() if len(parts) > 1 else ''
        
        print(f"  Key name: {key_name}")
        print(f"  Key value: {key_value}")
        
        # Try to decode if it looks like Base64
        if key_value and '=' in key_value:
            try:
                decoded_key = base64.b64decode(key_value)
                print(f"  Decoded: {decoded_key}")
                print(f"  Decoded (string): {decoded_key.decode('utf-8', errors='ignore')}")
            except:
                pass

# Now let's look for the REAL key
print("\n" + "="*60)
print("[*] Looking for the REAL key in the file...")

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

# The pattern shows: KEY____________:V1JPTkdLRVk=
# Let's look for other similar patterns
key_patterns = re.findall(rb'KEY[_\s]{0,20}:[A-Za-z0-9+/=]{5,}', data)
print(f"[+] Found {len(key_patterns)} KEY patterns:")
for pattern in key_patterns:
    print(f"    {pattern}")
    
    # Extract and decode the Base64 part
    match = re.search(rb':([A-Za-z0-9+/=]+)', pattern)
    if match:
        b64_data = match.group(1)
        try:
            decoded_key = base64.b64decode(b64_data)
            print(f"        Decoded: {decoded_key.decode('utf-8', errors='ignore')}")
        except:
            pass

# Look for any other Base64 that's NOT WRONGKEY
print("\n[*] Looking for other Base64 strings...")
all_b64 = re.findall(rb'[A-Za-z0-9+/]{16,}={0,2}', data)
for b64 in all_b64:
    if b64 != b'V1JPTkdLRVk=':  # Skip the WRONGKEY
        try:
            decoded = base64.b64decode(b64)
            if decoded.isascii() and len(decoded) > 4:
                decoded_str = decoded.decode('utf-8', errors='ignore')
                if any(c.isalpha() for c in decoded_str):
                    print(f"    {b64[:40]} -> {decoded_str}")
                    
                    # Check if this could be a key
                    if 'KEY' in decoded_str.upper() or len(decoded_str) == 8:
                        print(f"        ^^^ POTENTIAL KEY!")
        except:
            pass

print("\n[*] Analysis complete!")
