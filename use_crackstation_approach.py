#!/usr/bin/env python3
"""
Use hash cracking approaches from CTF_tools repo
CrackStation is mentioned as the go-to tool for SHA1 hashes
"""

import hashlib
import requests
import time

target_hash = "707b10ba2d8020957997e4127c99147091087a71"

print("="*70)
print("HASH CRACKING WITH CTF TOOLS APPROACH")
print("="*70)
print(f"\nTarget SHA-1 Hash: {target_hash}")

# According to CTF_tools, CrackStation is the best for SHA1
# But we can't directly query their API, so let's try other approaches

# Method 1: Try hashes.com API
print("\n" + "="*70)
print("METHOD 1: Hashes.com Lookup")
print("="*70)

try:
    # hashes.com has a free API
    url = f"https://hashes.com/en/api/identifier"
    # Note: This is just identifier, not cracker
    
    # Let's try their decrypt API
    # Format: https://hashes.com/en/decrypt/hash
    print(f"\nYou can manually check: https://hashes.com/en/decrypt/hash")
    print(f"Hash to check: {target_hash}")
except Exception as e:
    print(f"Error: {e}")

# Method 2: Try common CTF passwords
print("\n" + "="*70)
print("METHOD 2: CTF-Specific Passwords")
print("="*70)

# Based on CTF experience, try CTF-specific patterns
ctf_specific = [
    # Flag formats
    'flag', 'FLAG', 'Flag', 'flag{', 'FLAG{', 'Kaal{',
    
    # Common CTF words
    'ctf', 'CTF', 'Ctf', 'capture', 'theflag', 'picoctf', 'hackthebox',
    
    # Challenge-specific (betrayal theme)
    'betrayal', 'employee', 'stolen', 'data', 'disk', 'hidden',
    'location', 'storage', 'device', 'recover', 'information',
    
    # Author names
    'Le0', 'leo', 'LEO', 'le0', 'Haardik', 'haardik', 'Bhagtani', 'bhagtani',
    
    # Platform
    'vercel', 'Vercel', 'VERCEL',
    
    # Common CTF passwords from experience
    'admin', 'password', 'root', 'toor', 'guest', 'user',
    '123456', 'password123', 'admin123', 'root123',
    
    # Opposite of hello (username)
    'goodbye', 'bye', 'world', 'there',
    
    # Simple combinations
    'helloworld', 'worldhello', 'hello123', 'world123',
    'admin@123', 'admin@321', 'password!', 'password@123',
]

print("\nTrying CTF-specific passwords...")
for pwd in ctf_specific:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND: {pwd} ***")
        print(f"Hash: {h}")
        exit(0)

# Method 3: Try with rockyou patterns
print("\n" + "="*70)
print("METHOD 3: Rockyou-Style Patterns")
print("="*70)

# Most common from rockyou that we might have missed
rockyou_extended = [
    'password', '123456', '12345678', 'qwerty', 'abc123', 'monkey',
    'letmein', 'trustno1', 'dragon', 'baseball', 'iloveyou', 'master',
    'sunshine', 'ashley', 'bailey', 'passw0rd', 'shadow', 'superman',
    'qazwsx', '123123', 'welcome', 'login', 'admin', 'princess', 'solo',
    'qwertyuiop', 'starwars', 'password1', '123qwe', 'zxcvbnm', '121212',
    'freedom', 'whatever', 'nicole', 'jordan', 'michelle', 'hunter',
    'buster', 'soccer', 'harley', 'batman', 'andrew', 'tigger', 'charlie',
    'robert', 'thomas', 'hockey', 'ranger', 'daniel', 'starwars', 'klaster',
    '112233', 'george', 'asshole', 'computer', 'michelle', 'jessica',
    'pepper', '1111', 'zxcvbn', '555555', '11111111', '131313', '777777',
    'pass', 'maggie', '159753', 'aaaaaa', 'ginger', 'princess', 'joshua',
    'cheese', 'amanda', 'summer', 'love', 'ashley', 'nicole', 'chelsea',
    'biteme', 'matthew', 'access', 'yankees', '987654321', 'dallas',
    'austin', 'thunder', 'taylor', 'matrix', 'william', 'corvette',
    'hello', 'martin', 'heather', 'secret', 'fucker', 'merlin', 'diamond',
    'michael', 'fuckme', 'francisco', 'hockey', 'shit', 'iceman', 'money',
    'london', 'tennis', '999999', 'ncc1701', 'coffee', 'scooter', '0000',
    'miller', 'boston', 'q1w2e3r4', 'brandon', 'yamaha', 'chester',
    'mother', 'forever', 'johnny', 'edward', 'oliver', '333333', 'nathan',
    'carolina', 'stephen', 'rabbit', 'crystal', 'barney', 'xxxxxx',
    'steven', 'ranger', 'patrick', 'internet', 'kennedy', 'guinness',
    'casper', 'james', 'rachel', 'green', 'racing', 'mercedes', 'service',
    'brandon', 'fender', 'lakers', 'matthew', 'qwerty123', 'time',
    'sydney', 'midnight', 'xxxxxxxx', 'brittany', 'jack', 'apple',
    'scorpio', 'doctor', 'aaaaa', 'whatever', 'chicken', 'shelby',
    'sierra', 'peaches', 'gemini', 'doctor', 'wilson', 'sandra', 'helpme',
    'qwertyui', 'victor', 'florida', 'dolphin', 'pookie', 'captain',
    'tucker', 'blue', 'liverpool', 'theman', 'bandit', 'dolphins',
    'maddog', 'packers', 'jaguar', 'lovers', 'nicholas', 'united',
    'tiffany', 'maxwell', 'zzzzzz', 'nirvana', 'jeremy', 'monica',
    'elephant', 'giants', 'hotdog', 'rosebud', 'success', 'debbie',
    'mountain', '444444', 'xxxxxxxx', 'warrior', 'rainbow', 'johnny',
    'arthur', 'cream', 'calvin', 'shaved', 'surfer', 'samson', 'kelly',
    'paul', 'mine', 'king', 'racing', '5555', 'eagle', 'hentai',
    'newyork', 'little', 'redwings', 'smith', 'sticky', 'cocacola',
    'animal', 'broncos', 'private', 'skippy', 'marvin', 'blondes',
    'enjoy', 'girl', 'apollo', 'parker', 'qwert', 'time', 'sydney',
    'women', 'voodoo', 'magnum', 'juice', 'abgrtyu', '777777', 'dreams',
    'maxwell', 'music', 'rush2112', 'russia', 'scorpio', 'rebecca',
    'tester', 'mistress', 'phantom', 'billy', '6666', 'albert'
]

print("\nTrying extended rockyou passwords...")
for pwd in rockyou_extended:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND: {pwd} ***")
        print(f"Hash: {h}")
        exit(0)

# Method 4: Check if it's a known hash online
print("\n" + "="*70)
print("METHOD 4: Online Hash Databases")
print("="*70)

print("\nThe hash might be in online databases. Check these:")
print(f"  1. CrackStation: https://crackstation.net/")
print(f"  2. Hashes.com: https://hashes.com/en/decrypt/hash")
print(f"  3. MD5Decrypt: https://md5decrypt.net/en/Sha1/")
print(f"  4. HashKiller: https://hashkiller.io/listmanager")
print(f"\nHash to check: {target_hash}")

# Method 5: Try simple transformations of "hello"
print("\n" + "="*70)
print("METHOD 5: Transformations of 'hello' (username)")
print("="*70)

hello_transforms = []
base = 'hello'

# Add numbers
for i in range(1000):
    hello_transforms.append(f"{base}{i}")
    hello_transforms.append(f"{i}{base}")

# Add special chars
special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
for char in special:
    hello_transforms.append(f"{base}{char}")
    hello_transforms.append(f"{char}{base}")

# Add common suffixes
suffixes = ['123', '321', '1234', '12345', '!', '@', '#', '$$', '**']
for suffix in suffixes:
    hello_transforms.append(f"{base}{suffix}")

print(f"\nTrying {len(hello_transforms)} transformations of 'hello'...")
for pwd in hello_transforms:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND: {pwd} ***")
        print(f"Hash: {h}")
        exit(0)

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("\nPassword not found in common lists.")
print("The password likely requires:")
print("  1. Full rockyou.txt wordlist (14M+ passwords)")
print("  2. Online hash cracking service (CrackStation recommended)")
print("  3. Custom wordlist based on challenge context")
print("\nRecommended: Use CrackStation.net to crack this hash")
