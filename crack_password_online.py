#!/usr/bin/env python3
"""
Try to crack the password hash using various methods
Hash: 707b10ba2d8020957997e4127c99147091087a71
"""

import hashlib
import itertools
import string

target_hash = "707b10ba2d8020957997e4127c99147091087a71"

print("="*70)
print("PASSWORD HASH CRACKING ATTEMPT")
print("="*70)
print(f"Target: {target_hash}")

# Try common CTF-related passwords
ctf_passwords = [
    'kaal', 'Kaal', 'KAAL', 'kaalchakra', 'Kaalchakra', 'KAALCHAKRA',
    'betrayal', 'Betrayal', 'BETRAYAL', 'employee', 'Employee',
    'stolen', 'Stolen', 'data', 'Data', 'disk', 'Disk',
    'confidential', 'Confidential', 'hidden', 'Hidden',
    'flag', 'Flag', 'FLAG', 'ctf', 'CTF',
    'admin', 'Admin', 'ADMIN', 'password', 'Password',
    'world', 'World', 'WORLD', 'helloworld', 'HelloWorld',
    'hello123', 'Hello123', 'admin123', 'Admin123',
    'betrayal123', 'employee123', 'stolen123',
    'Le0', 'le0', 'LE0', 'Haardik', 'haardik',
    'fury', 'Fury', 'FURY', 'shield', 'Shield', 'SHIELD',
    'kolkata', 'Kolkata', 'KOLKATA',
    'vercel', 'Vercel', 'VERCEL',
    'login', 'Login', 'LOGIN',
    'auth', 'Auth', 'AUTH',
    'secret', 'Secret', 'SECRET',
    'key', 'Key', 'KEY',
    'token', 'Token', 'TOKEN',
    'encrypted', 'Encrypted', 'ENCRYPTED',
    'decrypt', 'Decrypt', 'DECRYPT',
    'hard', 'Hard', 'HARD',
    'storage', 'Storage', 'STORAGE',
    'device', 'Device', 'DEVICE',
    'recover', 'Recover', 'RECOVER',
    'location', 'Location', 'LOCATION',
    'information', 'Information', 'INFORMATION',
    'trust', 'Trust', 'TRUST',
    'system', 'System', 'SYSTEM',
    'clue', 'Clue', 'CLUE',
    'website', 'Website', 'WEBSITE',
    'link', 'Link', 'LINK',
    'text', 'Text', 'TEXT',
    'attempt', 'Attempt', 'ATTEMPT',
    'method', 'Method', 'METHOD',
    'external', 'External', 'EXTERNAL',
    'copy', 'Copy', 'COPY',
    'present', 'Present', 'PRESENT',
    'identify', 'Identify', 'IDENTIFY',
    'retrieve', 'Retrieve', 'RETRIEVE',
]

print("\n1. Trying CTF-related passwords...")
for pwd in ctf_passwords:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND: {pwd} ***")
        exit(0)

# Try numeric passwords
print("\n2. Trying numeric passwords (0-9999)...")
for i in range(10000):
    pwd = str(i)
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND: {pwd} ***")
        exit(0)

# Try simple combinations
print("\n3. Trying simple combinations...")
simple_words = ['hello', 'world', 'admin', 'kaal', 'betrayal', 'flag']
for word1 in simple_words:
    for word2 in simple_words:
        if word1 != word2:
            pwd = word1 + word2
            h = hashlib.sha1(pwd.encode()).hexdigest()
            if h == target_hash:
                print(f"\n*** PASSWORD FOUND: {pwd} ***")
                exit(0)

# Try with numbers
print("\n4. Trying words with numbers...")
for word in simple_words:
    for i in range(1000):
        pwd = word + str(i)
        h = hashlib.sha1(pwd.encode()).hexdigest()
        if h == target_hash:
            print(f"\n*** PASSWORD FOUND: {pwd} ***")
            exit(0)
        
        pwd = str(i) + word
        h = hashlib.sha1(pwd.encode()).hexdigest()
        if h == target_hash:
            print(f"\n*** PASSWORD FOUND: {pwd} ***")
            exit(0)

# Try short alphanumeric passwords (3-5 chars)
print("\n5. Trying short alphanumeric passwords (3-4 chars)...")
chars = string.ascii_lowercase + string.digits

for length in [3, 4]:
    print(f"   Trying length {length}...")
    count = 0
    for combo in itertools.product(chars, repeat=length):
        pwd = ''.join(combo)
        h = hashlib.sha1(pwd.encode()).hexdigest()
        if h == target_hash:
            print(f"\n*** PASSWORD FOUND: {pwd} ***")
            exit(0)
        
        count += 1
        if count % 10000 == 0:
            print(f"   Tried {count} combinations...", end='\r')

print("\n\nPassword not found in common lists.")
print("The password might be in a larger wordlist like rockyou.txt")
print("\nYou can try online hash crackers:")
print("  - https://crackstation.net/")
print("  - https://hashes.com/en/decrypt/hash")
print("  - https://md5decrypt.net/en/Sha1/")
