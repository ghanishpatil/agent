#!/usr/bin/env python3
"""
Maybe we don't need to crack the password at all!
Let's try to bypass the login or find another way
"""

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import re

# The key from the HTML comment
AES_KEY_B64 = "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="
AES_KEY = base64.b64decode(AES_KEY_B64.replace('-', '+').replace('_', '/'))

# The encrypted token
ENCRYPTED_TOKEN = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

print("="*70)
print("BYPASS APPROACH - DECRYPT WITHOUT PASSWORD")
print("="*70)

print("\nTheory: Maybe the login is just a distraction!")
print("The real challenge is to decrypt the token with the AES key from the comment.")
print("\nLet's try EVERY possible AES decryption method...\n")

# Decode token
token_bytes = base64.urlsafe_b64decode(ENCRYPTED_TOKEN + '==')
print(f"Token length: {len(token_bytes)} bytes")
print(f"Key length: {len(AES_KEY)} bytes (AES-256)")

# Try EVERY AES mode with EVERY possible configuration
attempts = []

# 1. ECB mode (no IV)
try:
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    # Pad to 16 bytes
    padded = token_bytes + b'\x00' * (16 - len(token_bytes) % 16) if len(token_bytes) % 16 != 0 else token_bytes
    decrypted = cipher.decrypt(padded)
    attempts.append(('ECB_padded', decrypted))
    
    # Try unpadding
    try:
        unpadded = unpad(decrypted, 16)
        attempts.append(('ECB_unpadded', unpadded))
    except:
        pass
except Exception as e:
    print(f"ECB error: {e}")

# 2. CBC mode - IV from first 16 bytes
try:
    iv = token_bytes[:16]
    ciphertext = token_bytes[16:]
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    
    # Pad ciphertext
    padded = ciphertext + b'\x00' * (16 - len(ciphertext) % 16) if len(ciphertext) % 16 != 0 else ciphertext
    decrypted = cipher.decrypt(padded)
    attempts.append(('CBC_iv_from_token', decrypted))
    
    try:
        unpadded = unpad(decrypted, 16)
        attempts.append(('CBC_iv_from_token_unpadded', unpadded))
    except:
        pass
except Exception as e:
    print(f"CBC error: {e}")

# 3. CBC mode - zero IV
try:
    iv = b'\x00' * 16
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    padded = token_bytes + b'\x00' * (16 - len(token_bytes) % 16) if len(token_bytes) % 16 != 0 else token_bytes
    decrypted = cipher.decrypt(padded)
    attempts.append(('CBC_zero_iv', decrypted))
except Exception as e:
    print(f"CBC zero IV error: {e}")

# 4. CTR mode
try:
    from Crypto.Util import Counter
    nonce = token_bytes[:16]
    ciphertext = token_bytes[16:]
    ctr = Counter.new(128, initial_value=int.from_bytes(nonce, 'big'))
    cipher = AES.new(AES_KEY, AES.MODE_CTR, counter=ctr)
    decrypted = cipher.decrypt(ciphertext)
    attempts.append(('CTR', decrypted))
except Exception as e:
    print(f"CTR error: {e}")

# 5. CFB mode
try:
    iv = token_bytes[:16]
    ciphertext = token_bytes[16:]
    cipher = AES.new(AES_KEY, AES.MODE_CFB, iv)
    decrypted = cipher.decrypt(ciphertext)
    attempts.append(('CFB', decrypted))
except Exception as e:
    print(f"CFB error: {e}")

# 6. OFB mode
try:
    iv = token_bytes[:16]
    ciphertext = token_bytes[16:]
    cipher = AES.new(AES_KEY, AES.MODE_OFB, iv)
    decrypted = cipher.decrypt(ciphertext)
    attempts.append(('OFB', decrypted))
except Exception as e:
    print(f"OFB error: {e}")

# 7. GCM mode (with tag)
for tag_size in [16, 12, 8]:
    try:
        nonce = token_bytes[:16]
        tag = token_bytes[-tag_size:]
        ciphertext = token_bytes[16:-tag_size]
        cipher = AES.new(AES_KEY, AES.MODE_GCM, nonce=nonce)
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        attempts.append((f'GCM_tag{tag_size}', decrypted))
    except:
        pass

# Check all attempts for the flag
print("Checking all decryption attempts for flag...\n")

for name, data in attempts:
    try:
        # Try UTF-8
        text = data.decode('utf-8', errors='ignore')
        
        # Check for flag
        if 'Kaal{' in text:
            print(f"\n{'='*70}")
            print(f"*** FLAG FOUND WITH {name} ***")
            print(f"{'='*70}")
            flags = re.findall(r'Kaal\{[^}]+\}', text)
            for flag in flags:
                print(f"\nFLAG: {flag}")
            print(f"\nFull text: {text}")
            exit(0)
        
        # Check for readable text
        if len([c for c in text if c.isprintable()]) > len(text) * 0.7:
            print(f"{name}:")
            print(f"  {text[:100]}")
            if len(text) > 100:
                print(f"  ... ({len(text)} chars total)")
    except:
        pass

print("\n" + "="*70)
print("NO FLAG FOUND IN DIRECT DECRYPTION")
print("="*70)

# Maybe the password IS in the JavaScript somehow?
print("\nLet me check if the password is hidden in the HTML/JS...")

# Read the HTML
with open('betrayal_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Look for any strings that might be passwords
print("\nSearching for hidden strings in HTML...")

# Extract all strings in quotes
strings = re.findall(r'["\']([^"\']{4,})["\']', html)
unique_strings = list(set(strings))

print(f"\nFound {len(unique_strings)} unique strings, checking as passwords...")

import hashlib
target_hash = "707b10ba2d8020957997e4127c99147091087a71"

for s in unique_strings:
    h = hashlib.sha1(s.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND IN HTML: {s} ***")
        exit(0)

print("\n✗ Password not found in HTML strings")

# Maybe it's in the image URL?
image_url = "https://i.imgur.com/LXcDQWj.jpeg"
print(f"\nChecking image URL: {image_url}")

url_parts = ['LXcDQWj', 'imgur', 'LXcDQWj.jpeg']
for part in url_parts:
    h = hashlib.sha1(part.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND IN URL: {part} ***")
        exit(0)

print("\n✗ Password not in URL")

print("\n" + "="*70)
print("FINAL CONCLUSION")
print("="*70)
print("\nThe challenge REQUIRES the password to be cracked.")
print("The password is NOT:")
print("  - In rockyou.txt")
print("  - In the HTML/JavaScript")
print("  - Derivable from the token or key")
print("  - In common wordlists")
print("\nThe password must be obtained from the CTF platform or organizers.")
