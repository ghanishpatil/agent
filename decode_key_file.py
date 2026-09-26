#!/usr/bin/env python3
"""Decode the key file"""

KEY_FILE = "apk_extracted/embedded_2.bin"

with open(KEY_FILE, 'rb') as f:
    data = f.read()

print("="*80)
print("DECODING KEY FILE")
print("="*80)

print(f"\nFile size: {len(data)} bytes")
print(f"Raw data: {data}")

# The data before the key looks like Unicode
# \xdb\x9f\xdb\xa1 etc. - these are Arabic diacritical marks

# Split at the key
key_start = data.find(b'401745546b5c0affd89343914f88bab4c82')
before_key = data[:key_start]
key = data[key_start:key_start+35]
after_key = data[key_start+35:]

print(f"\nBefore key ({len(before_key)} bytes): {before_key}")
print(f"Key ({len(key)} bytes): {key}")
print(f"After key ({len(after_key)} bytes): {after_key}")

# Try to decode the before_key part
print("\n[Trying to decode the prefix]")

# It might be UTF-8
try:
    decoded = before_key.decode('utf-8')
    print(f"UTF-8: {decoded}")
    print(f"Repr: {repr(decoded)}")
except Exception as e:
    print(f"UTF-8 failed: {e}")

# The pattern \xdb\x9f\xdb\xa1 etc. - these are Arabic combining marks
# Let's see if they encode something

# Extract just the second byte of each pair
extracted = []
for i in range(0, len(before_key), 2):
    if i+1 < len(before_key):
        extracted.append(before_key[i+1])

print(f"\nExtracted bytes: {bytes(extracted)}")
print(f"As ASCII: {bytes(extracted).decode('ascii', errors='ignore')}")

# Try as hex
hex_str = ''.join(f'{b:02x}' for b in extracted)
print(f"As hex string: {hex_str}")

# Maybe it's the password!
password_candidate = bytes(extracted).decode('ascii', errors='ignore')
print(f"\n✓✓✓ POSSIBLE PASSWORD: {password_candidate}")

print("\n" + "="*80)
