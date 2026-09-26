#!/usr/bin/env python3
"""
Crack the login credentials from the HTML
Username hash: aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d
Password hash: 707b10ba2d8020957997e4127c99147091087a71
Comment in code: "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="
"""

import hashlib
import requests
import base64

# The hashes from the HTML
username_hash = "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
password_hash = "707b10ba2d8020957997e4127c99147091087a71"

# The comment that looks like base64
comment = "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="

print("="*70)
print("CRACKING LOGIN CREDENTIALS")
print("="*70)

# Step 1: Try to crack the hashes with common passwords
print("\n1. Trying common passwords:")

common_passwords = [
    'admin', 'password', 'hello', '123456', 'admin123', 'root', 'test',
    'user', 'guest', 'kaal', 'kaalchakra', 'ctf', 'flag', 'betrayal',
    'employee', 'data', 'stolen', 'disk', 'storage', 'confidential'
]

username = None
password = None

for word in common_passwords:
    h = hashlib.sha1(word.encode()).hexdigest()
    if h == username_hash:
        username = word
        print(f"   ✓ Username found: {word}")
    if h == password_hash:
        password = word
        print(f"   ✓ Password found: {word}")

# Step 2: Try online hash lookup
print("\n2. Hash analysis:")
print(f"   Username hash: {username_hash}")
print(f"   Password hash: {password_hash}")

# These are SHA-1 hashes, let me try to crack them
# aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d is SHA-1 of "hello"
# Let me verify

test = hashlib.sha1("hello".encode()).hexdigest()
if test == username_hash:
    username = "hello"
    print(f"   ✓ Username is: hello")

# Try more passwords
password_list = [
    'world', 'admin', 'password', '12345', 'qwerty', 'letmein',
    'welcome', 'monkey', 'dragon', 'master', 'sunshine', 'princess',
    'football', 'shadow', 'michael', 'jennifer', 'computer', 'secret'
]

for pwd in password_list:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == password_hash:
        password = pwd
        print(f"   ✓ Password is: {pwd}")
        break

# Step 3: Analyze the comment
print("\n3. Analyzing the comment:")
print(f"   Comment: {comment}")

# Try to decode as base64
try:
    decoded = base64.b64decode(comment.replace('-', '+').replace('_', '/'))
    print(f"   Decoded: {decoded}")
    print(f"   As hex: {decoded.hex()}")
    
    # This might be the password or a key
    # Try it as password
    h = hashlib.sha1(comment.encode()).hexdigest()
    if h == password_hash:
        password = comment
        print(f"   ✓ Comment is the password!")
        
except Exception as e:
    print(f"   Error: {e}")

# Step 4: If we have credentials, try to login
if username and password:
    print(f"\n4. Credentials found!")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    
    # Now we need to actually login to the website
    # But the login is client-side JavaScript
    # We need to look for what happens after successful login
    
else:
    print(f"\n4. Need to crack the hashes...")
    print(f"   Trying rockyou wordlist approach...")
    
    # Let me try a broader search
    import string
    
    # Try short passwords (3-6 chars)
    print("   Trying short passwords...")
    
    # Actually, let me check if these are known hashes
    # aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d = "hello"
    # 707b10ba2d8020957997e4127c99147091087a71 = ?
    
    # Let me try the encrypted token as password
    encrypted_token = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"
    
    h = hashlib.sha1(encrypted_token.encode()).hexdigest()
    if h == password_hash:
        password = encrypted_token
        print(f"   ✓ Encrypted token is the password!")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Username: {username if username else 'UNKNOWN'}")
print(f"Password: {password if password else 'UNKNOWN'}")

if not password:
    print("\nTrying to crack password hash with online tools...")
    print(f"Hash: {password_hash}")
    print("This is SHA-1 hash")
