#!/usr/bin/env python3
"""
Final attempt to solve the game challenge
We know:
1. Target score: 0x12C (300)
2. Encoded flag: AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc
3. There are decode functions: a1, a2, a3, a4, d1, d2
4. fetch_flag and parse_flag functions exist

Strategy: Try to decode the flag string using common algorithms
"""

import base64
import string

encoded = "AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc"

print("="*80)
print("GAME REVERSE ENGINEERING - FINAL SOLVE")
print("="*80)

print(f"\nEncoded string: {encoded}")
print(f"Length: {len(encoded)}")

# Analyze the string
print("\n[Character Analysis]")
print(f"Unique characters: {set(encoded)}")
print(f"Character types:")
print(f"  - Uppercase: {sum(1 for c in encoded if c.isupper())}")
print(f"  - Lowercase: {sum(1 for c in encoded if c.islower())}")
print(f"  - Digits: {sum(1 for c in encoded if c.isdigit())}")
print(f"  - Underscores: {encoded.count('_')}")

# This looks like base64 with a custom alphabet
# Standard base64 alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
# Our string uses: A-Z, a-z, 0-9, _

print("\n[Attempt 1: Standard Base64]")
try:
    # Try adding padding
    for padding in ['', '=', '==', '===']:
        try:
            decoded = base64.b64decode(encoded + padding)
            print(f"  With padding '{padding}': {decoded}")
            if b'Kaal{' in decoded or b'kaal{' in decoded.lower():
                print(f"  ✓ FOUND FLAG: {decoded.decode('utf-8', errors='ignore')}")
        except:
            pass
except Exception as e:
    print(f"  Failed: {e}")

print("\n[Attempt 2: Base64 with _ as +]")
try:
    # Replace _ with + (common base64 variant)
    modified = encoded.replace('_', '+')
    for padding in ['', '=', '==', '===']:
        try:
            decoded = base64.b64decode(modified + padding)
            print(f"  With padding '{padding}': {decoded}")
            if b'Kaal{' in decoded or b'kaal{' in decoded.lower():
                print(f"  ✓ FOUND FLAG: {decoded.decode('utf-8', errors='ignore')}")
        except:
            pass
except Exception as e:
    print(f"  Failed: {e}")

print("\n[Attempt 3: Base64 with _ as /]")
try:
    # Replace _ with / (another variant)
    modified = encoded.replace('_', '/')
    for padding in ['', '=', '==', '===']:
        try:
            decoded = base64.b64decode(modified + padding)
            print(f"  With padding '{padding}': {decoded}")
            if b'Kaal{' in decoded or b'kaal{' in decoded.lower():
                print(f"  ✓ FOUND FLAG: {decoded.decode('utf-8', errors='ignore')}")
        except:
            pass
except Exception as e:
    print(f"  Failed: {e}")

print("\n[Attempt 4: URL-safe Base64]")
try:
    # URL-safe base64 uses - and _ instead of + and /
    for padding in ['', '=', '==', '===']:
        try:
            decoded = base64.urlsafe_b64decode(encoded + padding)
            print(f"  With padding '{padding}': {decoded}")
            if b'Kaal{' in decoded or b'kaal{' in decoded.lower():
                print(f"  ✓ FOUND FLAG: {decoded.decode('utf-8', errors='ignore')}")
        except:
            pass
except Exception as e:
    print(f"  Failed: {e}")

print("\n[Attempt 5: Custom Base64 Alphabet]")
# Try different alphabet permutations
standard_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
custom_alphabets = [
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_+",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_",
]

for custom_alpha in custom_alphabets:
    try:
        # Create translation table
        trans = str.maketrans(custom_alpha, standard_alphabet)
        translated = encoded.translate(trans)
        
        for padding in ['', '=', '==', '===']:
            try:
                decoded = base64.b64decode(translated + padding)
                if decoded and len(decoded) > 5:
                    print(f"  Alphabet {custom_alpha[-2:]}: {decoded}")
                    if b'Kaal{' in decoded or b'kaal{' in decoded.lower():
                        print(f"  ✓ FOUND FLAG: {decoded.decode('utf-8', errors='ignore')}")
            except:
                pass
    except:
        pass

print("\n[Attempt 6: XOR with common keys]")
# Try XOR with single-byte keys
encoded_bytes = encoded.encode()
for key in range(256):
    try:
        decoded = bytes([b ^ key for b in encoded_bytes])
        if b'Kaal{' in decoded:
            print(f"  XOR key {key} (0x{key:02x}): {decoded.decode('utf-8', errors='ignore')}")
            print(f"  ✓ FOUND FLAG!")
    except:
        pass

print("\n[Attempt 7: ROT13 and Caesar Cipher]")
# Try ROT13
result = ''
for char in encoded:
    if char.isalpha():
        if char.islower():
            result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
        else:
            result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
    else:
        result += char
print(f"  ROT13: {result}")

print("\n[Attempt 8: Reverse the string]")
reversed_str = encoded[::-1]
print(f"  Reversed: {reversed_str}")
# Try base64 decode on reversed
try:
    for padding in ['', '=', '==']:
        try:
            decoded = base64.b64decode(reversed_str + padding)
            if decoded:
                print(f"    Base64 of reversed: {decoded}")
        except:
            pass
except:
    pass

print("\n" + "="*80)
print("If none of these worked, we need to:")
print("1. Run the patched game.exe to trigger the decode function")
print("2. Or reverse engineer the actual decode algorithm from the binary")
print("="*80)
