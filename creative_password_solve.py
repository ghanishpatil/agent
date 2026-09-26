#!/usr/bin/env python3
"""
Creative approaches to find the password
"""

import hashlib
import base64

target_hash = "707b10ba2d8020957997e4127c99147091087a71"
username_hash = "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"  # = "hello"
comment = "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="

print("="*70)
print("CREATIVE PASSWORD SOLVING")
print("="*70)

# Idea 1: Maybe the password is related to "hello"
print("\n1. Passwords related to 'hello':")
hello_related = [
    'world', 'goodbye', 'hi', 'hey', 'greetings', 'welcome',
    'helloworld', 'worldhello', 'hello world', 'hello_world',
    'hello-world', 'hello.world', 'hello@world', 'hello!world',
    'helloWorld', 'HelloWorld', 'HELLOWORLD', 'Hello', 'HELLO'
]

for pwd in hello_related:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"   *** FOUND: {pwd} ***")
        exit(0)

# Idea 2: Maybe it's the comment itself or variations
print("\n2. Comment variations:")
comment_variations = [
    comment,
    comment.replace('=', ''),
    comment.replace('-', ''),
    comment.replace('_', ''),
    comment.lower(),
    comment.upper(),
]

for pwd in comment_variations:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"   *** FOUND: {pwd} ***")
        exit(0)

# Idea 3: Maybe it's the decoded comment
print("\n3. Decoded comment variations:")
try:
    decoded = base64.b64decode(comment.replace('-', '+').replace('_', '/'))
    decoded_variations = [
        decoded.hex(),
        decoded.hex().upper(),
        decoded.hex().lower(),
        str(decoded),
        decoded.decode('utf-8', errors='ignore'),
    ]
    
    for pwd in decoded_variations:
        h = hashlib.sha1(pwd.encode()).hexdigest()
        if h == target_hash:
            print(f"   *** FOUND: {pwd} ***")
            exit(0)
except:
    pass

# Idea 4: Maybe it's something from the encrypted token
print("\n4. Token variations:")
encrypted_token = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

# First few characters
for length in [4, 5, 6, 7, 8, 10, 12, 16, 20]:
    pwd = encrypted_token[:length]
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"   *** FOUND: {pwd} ***")
        exit(0)

# Idea 5: Maybe it's a simple word that we haven't tried
print("\n5. More simple words:")
simple_words = [
    'betrayal', 'employee', 'stolen', 'data', 'disk', 'hidden',
    'location', 'storage', 'device', 'recover', 'information',
    'confidential', 'trust', 'external', 'hard', 'clue', 'encrypted',
    'text', 'website', 'link', 'identify', 'retrieve', 'copy',
    'system', 'method', 'present', 'attempt', 'discover', 'later',
    'difficult', 'unfortunately', 'kolkata', 'vercel', 'login',
    'authorized', 'admin', 'welcome', 'successful', 'wrong',
    'credentials', 'remaining', 'blocked', 'contact', 'organisers',
    'unblock', 'flag', 'kaal', 'challenge', 'points', 'hard',
    'miscellaneous', 'category', 'author', 'le0', 'haardik',
    'bhagtani', 'international', 'level', 'ctf', 'format',
    'submit', 'details', 'tag', 'difficulty'
]

for word in simple_words:
    for variation in [word, word.capitalize(), word.upper(), word.lower()]:
        h = hashlib.sha1(variation.encode()).hexdigest()
        if h == target_hash:
            print(f"   *** FOUND: {variation} ***")
            exit(0)

# Idea 6: Maybe it's a phrase
print("\n6. Phrases:")
phrases = [
    'hello world', 'hello there', 'welcome admin', 'login successful',
    'authorized login', 'admin login', 'employee betrayal', 'stolen data',
    'hidden disk', 'hard disk', 'external storage', 'storage device',
    'encrypted text', 'website link', 'identify location', 'recover data',
    'confidential data', 'trust betrayed', 'data stolen', 'disk hidden',
    'location identified', 'information recovered', 'system blocked',
    'contact organisers', 'flag format', 'kaal flag', 'ctf challenge'
]

for phrase in phrases:
    for variation in [phrase, phrase.replace(' ', ''), phrase.replace(' ', '_'), phrase.replace(' ', '-')]:
        h = hashlib.sha1(variation.encode()).hexdigest()
        if h == target_hash:
            print(f"   *** FOUND: {variation} ***")
            exit(0)

# Idea 7: Maybe it's the hash itself or part of it
print("\n7. Hash variations:")
hash_variations = [
    target_hash,
    target_hash[:8],
    target_hash[:16],
    target_hash[:32],
    target_hash.upper(),
    username_hash,
    username_hash[:8],
]

for pwd in hash_variations:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"   *** FOUND: {pwd} ***")
        exit(0)

# Idea 8: Maybe it's a number
print("\n8. Numbers:")
for i in range(10000, 100000):
    pwd = str(i)
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"   *** FOUND: {pwd} ***")
        exit(0)
    
    if i % 10000 == 0:
        print(f"   Tried up to {i}...", end='\r')

print("\n\nPassword not found.")
print("\nNext steps:")
print("  1. Try full rockyou.txt wordlist")
print("  2. Use online hash cracking services")
print("  3. Check if there's a hint we're missing")
print("  4. Maybe the challenge requires actually logging in to see more clues")
