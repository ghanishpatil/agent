#!/usr/bin/env python3
"""
Alternative approach to crack the password
Looking at the challenge description and context clues
"""

import hashlib
import base64

target_hash = "707b10ba2d8020957997e4127c99147091087a71"
comment = "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="

print("="*70)
print("ALTERNATIVE PASSWORD CRACKING")
print("="*70)

# Challenge context: Employee betrayal, stolen data, hidden hard disks
# Author: Le0
# Points: 500 (Hard)
# Category: Miscellaneous

# Try passwords based on challenge context
context_passwords = [
    # From challenge description
    'employee', 'betrayed', 'betrayal', 'trust', 'stolen', 'confidential',
    'data', 'systems', 'external', 'storage', 'devices', 'hidden', 'hard',
    'disks', 'retrieve', 'encrypted', 'text', 'website', 'link', 'clue',
    'identify', 'location', 'recover', 'information',
    
    # Author name
    'Le0', 'leo', 'LEO', 'le0',
    
    # CTF name
    'Kaalchakra', 'kaalchakra', 'KAALCHAKRA', 'Kaal', 'kaal', 'KAAL',
    
    # Common variations
    'employee123', 'betrayal123', 'stolen123', 'data123',
    'le0123', 'kaal123', 'ctf123',
    
    # Vercel related (hosting platform)
    'vercel', 'Vercel', 'VERCEL',
    
    # Login related
    'admin', 'Admin', 'ADMIN', 'administrator', 'Administrator',
    'root', 'Root', 'ROOT', 'user', 'User', 'USER',
    
    # Security related
    'password', 'Password', 'PASSWORD', 'pass', 'Pass', 'PASS',
    'secret', 'Secret', 'SECRET', 'key', 'Key', 'KEY',
    
    # Opposite of hello
    'goodbye', 'Goodbye', 'GOODBYE', 'bye', 'Bye', 'BYE',
    
    # Common pairs with hello
    'world', 'World', 'WORLD', 'there', 'There', 'THERE',
    
    # Numbers that might be significant
    '500', '707', '2157869541235478521545895', '83927465839274658392746583',
    
    # Base64 comment itself
    comment,
    
    # Decoded comment as string
    base64.b64decode(comment.replace('-', '+').replace('_', '/')).hex(),
    
    # Try the encrypted token
    'SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7',
]

print("\nTrying context-based passwords...")
for pwd in context_passwords:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND: {pwd} ***")
        print(f"Hash: {h}")
        exit(0)

# Try combinations
print("\nTrying combinations...")
words = ['hello', 'world', 'admin', 'kaal', 'betrayal', 'le0', 'employee', 'stolen']
separators = ['', '_', '-', '.', '@', '#', '!']

for word1 in words:
    for word2 in words:
        if word1 != word2:
            for sep in separators:
                pwd = word1 + sep + word2
                h = hashlib.sha1(pwd.encode()).hexdigest()
                if h == target_hash:
                    print(f"\n*** PASSWORD FOUND: {pwd} ***")
                    exit(0)

# Try with years
print("\nTrying with years...")
for word in words:
    for year in range(2020, 2027):
        pwd = word + str(year)
        h = hashlib.sha1(pwd.encode()).hexdigest()
        if h == target_hash:
            print(f"\n*** PASSWORD FOUND: {pwd} ***")
            exit(0)
        
        pwd = str(year) + word
        h = hashlib.sha1(pwd.encode()).hexdigest()
        if h == target_hash:
            print(f"\n*** PASSWORD FOUND: {pwd} ***")
            exit(0)

# Try leetspeak variations
print("\nTrying leetspeak variations...")
leet_map = {
    'a': ['a', '4', '@'],
    'e': ['e', '3'],
    'i': ['i', '1', '!'],
    'o': ['o', '0'],
    's': ['s', '5', '$'],
    't': ['t', '7'],
    'l': ['l', '1'],
}

def generate_leet(word):
    variations = [word]
    for char, replacements in leet_map.items():
        new_variations = []
        for var in variations:
            for rep in replacements:
                new_variations.append(var.replace(char, rep))
        variations = new_variations
    return variations

for word in ['hello', 'world', 'admin', 'kaal', 'betrayal']:
    for leet_word in generate_leet(word):
        h = hashlib.sha1(leet_word.encode()).hexdigest()
        if h == target_hash:
            print(f"\n*** PASSWORD FOUND: {leet_word} ***")
            exit(0)

print("\nPassword not found with context-based attempts.")
print("\nThe password might require:")
print("  1. A larger wordlist (rockyou.txt)")
print("  2. Online hash cracking service")
print("  3. Looking at the actual website for more clues")
