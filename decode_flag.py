#!/usr/bin/env python3
"""
Decode the potential flag string
"""
import base64
import binascii

encoded = "AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc"

print("="*60)
print("DECODING FLAG")
print("="*60)

print(f"\nEncoded string: {encoded}")
print(f"Length: {len(encoded)}")

# Try base64 decode
print("\n[1] Base64 decode:")
try:
    decoded = base64.b64decode(encoded)
    print(f"    Decoded bytes: {decoded}")
    print(f"    As string: {decoded.decode('utf-8', errors='ignore')}")
except Exception as e:
    print(f"    Error: {e}")

# Try base64 with padding
print("\n[2] Base64 with padding:")
for padding in ['', '=', '==', '===']:
    try:
        decoded = base64.b64decode(encoded + padding)
        print(f"    Padding '{padding}': {decoded}")
        try:
            as_str = decoded.decode('utf-8')
            print(f"        As string: {as_str}")
            if 'Kaal' in as_str or '{' in as_str:
                print(f"        *** POTENTIAL FLAG: {as_str} ***")
        except:
            pass
    except Exception as e:
        pass

# Try hex decode
print("\n[3] Hex decode:")
try:
    decoded = binascii.unhexlify(encoded)
    print(f"    Decoded: {decoded}")
except Exception as e:
    print(f"    Error: {e}")

# Try ROT13
print("\n[4] ROT13:")
import codecs
decoded = codecs.decode(encoded, 'rot_13')
print(f"    Decoded: {decoded}")

# Try Caesar cipher
print("\n[5] Caesar cipher (shifts 1-25):")
for shift in range(1, 26):
    decoded = ''
    for c in encoded:
        if c.isalpha():
            if c.isupper():
                decoded += chr((ord(c) - ord('A') + shift) % 26 + ord('A'))
            else:
                decoded += chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
        else:
            decoded += c
    if 'Kaal' in decoded or 'kaal' in decoded.lower():
        print(f"    Shift {shift}: {decoded}")

# Try XOR with common keys
print("\n[6] XOR with common keys:")
for key in [0x42, 0x13, 0x37, 0xFF, 0xAA]:
    decoded = ''.join([chr(ord(c) ^ key) for c in encoded])
    if all(32 <= ord(c) < 127 for c in decoded):
        print(f"    Key 0x{key:02x}: {decoded}")

print("\n" + "="*60)
