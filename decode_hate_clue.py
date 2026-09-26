#!/usr/bin/env python3
"""Decode the HTML comment: U0kcfdLN_WhDhNldOLdHJ"""

import base64
import binascii

encoded = "U0kcfdLN_WhDhNldOLdHJ"

print("="*60)
print(f"Decoding: {encoded}")
print("="*60)

# Try base64 with padding
for padding in ['', '=', '==', '===']:
    try:
        decoded = base64.b64decode(encoded + padding)
        print(f"\nBase64 (padding '{padding}'): {decoded}")
        try:
            print(f"  As UTF-8: {decoded.decode('utf-8')}")
        except:
            print(f"  As hex: {decoded.hex()}")
    except Exception as e:
        pass

# Try URL-safe base64
for padding in ['', '=', '==', '===']:
    try:
        decoded = base64.urlsafe_b64decode(encoded + padding)
        print(f"\nURL-safe Base64 (padding '{padding}'): {decoded}")
        try:
            print(f"  As UTF-8: {decoded.decode('utf-8')}")
        except:
            print(f"  As hex: {decoded.hex()}")
    except Exception as e:
        pass

# Try base32
try:
    decoded = base64.b32decode(encoded + '====')
    print(f"\nBase32: {decoded}")
    print(f"  As UTF-8: {decoded.decode('utf-8')}")
except Exception as e:
    print(f"\nBase32 failed: {e}")

# Try hex
try:
    decoded = binascii.unhexlify(encoded)
    print(f"\nHex: {decoded}")
except Exception as e:
    pass

# Character analysis
print(f"\n\nCharacter Analysis:")
print(f"Length: {len(encoded)}")
print(f"Characters: {list(encoded)}")
print(f"ASCII values: {[ord(c) for c in encoded]}")

# Check if it's a path or endpoint
print(f"\n\nPossible paths to try:")
print(f"  /{encoded}")
print(f"  /api/{encoded}")
print(f"  /flag/{encoded}")
print(f"  /{encoded.lower()}")
print(f"  /{encoded.upper()}")

# Reverse
print(f"\n\nReversed: {encoded[::-1]}")

# ROT variations
import string
for rot in [13, 47]:
    result = ""
    for char in encoded:
        if char in string.ascii_uppercase:
            result += chr((ord(char) - ord('A') + rot) % 26 + ord('A'))
        elif char in string.ascii_lowercase:
            result += chr((ord(char) - ord('a') + rot) % 26 + ord('a'))
        else:
            result += char
    print(f"ROT{rot}: {result}")
