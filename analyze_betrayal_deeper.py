#!/usr/bin/env python3
"""
Deeper analysis of the betrayal challenge
The comment in the code: "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="
This looks like it might be a key or the actual password
"""

import hashlib
import base64
import requests

# The comment from the HTML
comment = "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="
target_hash = "707b10ba2d8020957997e4127c99147091087a71"

print("="*70)
print("DEEP ANALYSIS")
print("="*70)

# The comment is base64 - let's decode it
decoded = base64.b64decode(comment.replace('-', '+').replace('_', '/'))
print(f"\nComment decoded: {decoded.hex()}")

# This looks like it could be an AES key or similar
# Let me try using this to decrypt the encrypted token

encrypted_token = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

# Decode the encrypted token
token_decoded = base64.urlsafe_b64decode(encrypted_token + '==')
print(f"\nToken decoded length: {len(token_decoded)}")
print(f"Token hex: {token_decoded.hex()[:100]}...")

# Try AES decryption
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    
    key = decoded  # 32 bytes - perfect for AES-256
    
    # Try different modes
    # Mode 1: ECB
    try:
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = unpad(cipher.decrypt(token_decoded), AES.block_size)
        print(f"\nAES-ECB decrypted: {decrypted}")
        print(f"As text: {decrypted.decode('utf-8', errors='ignore')}")
        
        if b'Kaal{' in decrypted:
            print(f"\n*** FLAG FOUND: {decrypted.decode()} ***")
    except Exception as e:
        print(f"AES-ECB failed: {e}")
    
    # Mode 2: CBC (need IV)
    # Try using first 16 bytes as IV
    if len(token_decoded) > 16:
        iv = token_decoded[:16]
        ciphertext = token_decoded[16:]
        
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
            print(f"\nAES-CBC decrypted: {decrypted}")
            print(f"As text: {decrypted.decode('utf-8', errors='ignore')}")
            
            if b'Kaal{' in decrypted:
                print(f"\n*** FLAG FOUND: {decrypted.decode()} ***")
        except Exception as e:
            print(f"AES-CBC failed: {e}")
    
except ImportError:
    print("\nPyCryptodome not installed, trying alternative...")

# Maybe the password is just "world" (hello world)
test_passwords = ['world', 'helloworld', 'hello world', 'hello_world']
for pwd in test_passwords:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    print(f"{pwd}: {h}")
    if h == target_hash:
        print(f"\n*** PASSWORD IS: {pwd} ***")

# Check if there are other pages or endpoints
print("\n" + "="*70)
print("Checking for other endpoints...")
print("="*70)

url_base = "https://login-page-auqw.vercel.app"

endpoints = [
    '/',
    '/admin',
    '/dashboard',
    '/flag',
    '/api',
    '/login',
    '/decrypt',
    '/token',
    '/robots.txt',
    '/.well-known/security.txt',
    '/sitemap.xml'
]

for endpoint in endpoints:
    try:
        r = requests.get(url_base + endpoint, timeout=5)
        if r.status_code == 200 and len(r.text) > 100:
            print(f"  {endpoint}: {r.status_code} ({len(r.text)} bytes)")
            
            if 'Kaal{' in r.text:
                print(f"    *** FLAG FOUND IN {endpoint}! ***")
                import re
                flags = re.findall(r'Kaal\{[^}]+\}', r.text)
                for flag in flags:
                    print(f"    FLAG: {flag}")
    except:
        pass

print("\nDone")
