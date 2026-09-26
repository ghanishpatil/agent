#!/usr/bin/env python3
"""
Decode the encrypted token - might be JWT or contain password
"""

import base64
import json
import hashlib

encrypted_token = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

print("=" * 60)
print("DECODING ENCRYPTED TOKEN")
print("=" * 60)

# Check if it's a JWT (has dots)
if '.' in encrypted_token:
    print("[*] Looks like JWT format")
    parts = encrypted_token.split('.')
    for i, part in enumerate(parts):
        try:
            decoded = base64.urlsafe_b64decode(part + '==')
            print(f"\nPart {i}: {decoded}")
        except:
            pass

# Decode as base64
print("\n[*] Base64 decoding...")
try:
    token_standard = encrypted_token.replace('-', '+').replace('_', '/')
    padding = 4 - (len(token_standard) % 4)
    if padding != 4:
        token_standard += '=' * padding
    
    decoded = base64.b64decode(token_standard)
    print(f"Decoded bytes ({len(decoded)}): {decoded.hex()}")
    
    # Try to find ASCII strings
    ascii_chars = []
    for byte in decoded:
        if 32 <= byte <= 126:  # Printable ASCII
            ascii_chars.append(chr(byte))
        else:
            if ascii_chars:
                ascii_chars.append(' ')
    
    ascii_string = ''.join(ascii_chars).strip()
    print(f"\nPrintable ASCII: {ascii_string}")
    
    # Check if it contains "world" or other password hints
    if 'world' in ascii_string.lower():
        print("[+] Found 'world' in decoded data!")
    
    # Try XOR with common keys
    print("\n[*] Trying XOR decryption...")
    keys = [b'hello', b'world', b'key', b'password', b'secret']
    for key in keys:
        result = bytes([decoded[i] ^ key[i % len(key)] for i in range(len(decoded))])
        try:
            text = result.decode('utf-8', errors='ignore')
            if any(c.isalpha() for c in text):
                print(f"Key '{key.decode()}': {text[:100]}")
        except:
            pass
    
    # Check if decoded bytes hash to the password
    h = hashlib.sha1(decoded).hexdigest()
    print(f"\nSHA1 of decoded bytes: {h}")
    if h == '707b10ba2d8020957997e4127c99147091087a71':
        print("[+] DECODED BYTES ARE THE PASSWORD!")
        print(f"Password (hex): {decoded.hex()}")
        print(f"Password (raw): {decoded}")
    
    # Try as UTF-8
    try:
        text = decoded.decode('utf-8')
        print(f"\nUTF-8 decoded: {text}")
        h = hashlib.sha1(text.encode()).hexdigest()
        if h == '707b10ba2d8020957997e4127c99147091087a71':
            print(f"[+] PASSWORD FOUND: {text}")
    except:
        pass
    
    # Try as latin-1
    try:
        text = decoded.decode('latin-1')
        print(f"\nLatin-1 decoded: {text}")
        h = hashlib.sha1(text.encode('latin-1')).hexdigest()
        if h == '707b10ba2d8020957997e4127c99147091087a71':
            print(f"[+] PASSWORD FOUND: {text}")
    except:
        pass
    
except Exception as e:
    print(f"Error: {e}")

# The password might be "world" (hello world)
print("\n[*] Testing 'world' as password...")
h = hashlib.sha1(b'world').hexdigest()
print(f"SHA1('world'): {h}")
if h == '707b10ba2d8020957997e4127c99147091087a71':
    print("[+] PASSWORD IS: world")
    print("\n[+] CREDENTIALS:")
    print("    Username: hello")
    print("    Password: world")
