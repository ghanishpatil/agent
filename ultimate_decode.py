#!/usr/bin/env python3
"""
Ultimate decode attempt
Based on all analysis, try every possible decoding method
"""
import base64
import string
import itertools

encoded = "AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc"

print("="*60)
print("ULTIMATE DECODE - TRYING EVERYTHING")
print("="*60)

results = []

# 1. Base64 with all possible custom alphabets
print("\n[1] Custom base64 alphabets (systematic):")
std_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

# Try swapping different parts
variations = [
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",  # Standard
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_",  # URL-safe
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/",  # Lowercase first
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/",  # Digits first
    "zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA9876543210+/",  # Reversed
    "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm0123456789+/",  # ROT13 style
]

for i, custom_alphabet in enumerate(variations):
    trans_table = str.maketrans(custom_alphabet, std_alphabet)
    normalized = encoded.translate(trans_table)
    
    for padding in ['', '=', '==']:
        try:
            decoded = base64.b64decode(normalized + padding)
            decoded_str = decoded.decode('utf-8', errors='ignore')
            if decoded_str and len(decoded_str) > 3:
                if all(c in string.printable for c in decoded_str):
                    flag = f"Kaal{{{decoded_str}}}"
                    if flag not in results:
                        results.append(flag)
                        print(f"  Alphabet {i}: {flag}")
        except:
            pass

# 2. XOR with all single-byte keys
print("\n[2] XOR with single-byte keys (checking printable results):")
for key in range(256):
    decoded = ''.join([chr(ord(c) ^ key) for c in encoded])
    if all(c in string.printable for c in decoded) and len(decoded) > 10:
        flag = f"Kaal{{{decoded}}}"
        if flag not in results and ('_' in decoded or any(c.isdigit() for c in decoded)):
            results.append(flag)
            print(f"  Key 0x{key:02x}: {flag}")

# 3. Multi-byte XOR with common words
print("\n[3] Multi-byte XOR:")
xor_keys = [b'game', b'flag', b'kaal', b'ctf', b'score', b'win', b'play']
for key in xor_keys:
    decoded = ''.join([chr(ord(encoded[i]) ^ key[i % len(key)]) for i in range(len(encoded))])
    if all(c in string.printable for c in decoded):
        flag = f"Kaal{{{decoded}}}"
        if flag not in results:
            results.append(flag)
            print(f"  Key '{key.decode()}': {flag}")

# 4. Vigenere cipher
print("\n[4] Vigenere cipher:")
vigenere_keys = ['GAME', 'FLAG', 'KAAL', 'SCORE']
for key in vigenere_keys:
    decoded = ''
    for i, c in enumerate(encoded):
        if c.isalpha():
            key_char = key[i % len(key)]
            if c.isupper():
                decoded += chr((ord(c) - ord('A') - (ord(key_char) - ord('A'))) % 26 + ord('A'))
            else:
                decoded += chr((ord(c) - ord('a') - (ord(key_char.lower()) - ord('a'))) % 26 + ord('a'))
        else:
            decoded += c
    
    flag = f"Kaal{{{decoded}}}"
    if flag not in results:
        results.append(flag)
        print(f"  Key '{key}': {flag}")

# 5. The string might already be correct
print("\n[5] Direct usage:")
flag = f"Kaal{{{encoded}}}"
if flag not in results:
    results.append(flag)
    print(f"  {flag}")

# 6. Reverse the string
print("\n[6] Reversed:")
reversed_str = encoded[::-1]
flag = f"Kaal{{{reversed_str}}}"
if flag not in results:
    results.append(flag)
    print(f"  {flag}")

# 7. Base64 decode the reversed string
for padding in ['', '=', '==']:
    try:
        decoded = base64.b64decode(reversed_str + padding)
        decoded_str = decoded.decode('utf-8', errors='ignore')
        if decoded_str and all(c in string.printable for c in decoded_str):
            flag = f"Kaal{{{decoded_str}}}"
            if flag not in results:
                results.append(flag)
                print(f"  Reversed + base64: {flag}")
    except:
        pass

print("\n" + "="*60)
print(f"TOTAL CANDIDATES: {len(results)}")
print("="*60)
print("\nMOST LIKELY FLAGS:")
for i, flag in enumerate(results[:10], 1):
    print(f"{i}. {flag}")
print("="*60)
