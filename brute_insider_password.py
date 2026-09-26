#!/usr/bin/env python3
"""
Brute force common passwords for insider challenge
"""

import hashlib
import requests

target_hash = "707b10ba2d8020957997e4127c99147091087a71"

print("=" * 60)
print("BRUTE FORCING PASSWORD")
print("=" * 60)

# Extended wordlist based on challenge context
wordlist = []

# Challenge-specific words
base_words = [
    'betrayal', 'insider', 'employee', 'stolen', 'confidential',
    'data', 'storage', 'harddisk', 'external', 'hidden',
    'encrypted', 'token', 'trust', 'location', 'device',
    'kaalchakra', 'ctf', 'flag', 'challenge', 'le0',
    'hello', 'world', 'admin', 'password', 'secret',
    'key', 'code', 'access', 'login', 'auth'
]

# Add variations
for word in base_words:
    wordlist.append(word)
    wordlist.append(word.capitalize())
    wordlist.append(word.upper())
    wordlist.append(word + '123')
    wordlist.append(word + '7')
    wordlist.append(word + '2026')
    wordlist.append('123' + word)
    wordlist.append('7' + word)

# Add combinations
combinations = [
    'hello world', 'helloworld', 'hello_world', 'hello-world',
    'insider ctf', 'insiderctf', 'insider_ctf', 'insider-ctf',
    'insider7', 'insider ctf7', 'insiderctf7',
    'betrayal data', 'stolen data', 'hidden data',
    'external storage', 'hard disk', 'harddisk',
    'kaal chakra', 'kaalchakra', 'kaal_chakra',
    'le0 insider', 'le0insider', 'le0_insider'
]

wordlist.extend(combinations)

# Add numbers
for i in range(10000):
    wordlist.append(str(i))

print(f"[*] Testing {len(wordlist)} passwords...")

found = False
for i, pwd in enumerate(wordlist):
    if i % 1000 == 0:
        print(f"[*] Tested {i}/{len(wordlist)}...", end='\r')
    
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"\n\n[+] PASSWORD FOUND: {pwd}")
        print(f"[+] Hash: {h}")
        print(f"\n[+] CREDENTIALS:")
        print(f"    Username: hello")
        print(f"    Password: {pwd}")
        found = True
        break

if not found:
    print(f"\n\n[-] Password not found in {len(wordlist)} attempts")
    print("[!] Try online cracker: https://crackstation.net/")
    print(f"[!] Hash: {target_hash}")
    
    # Check if there are hints on the website
    print("\n[*] Checking website for additional hints...")
    try:
        url = "https://login-page-auqw.vercel.app"
        
        # Check robots.txt
        response = requests.get(url + '/robots.txt', timeout=5)
        if response.status_code == 200:
            print(f"\n[+] robots.txt found:")
            print(response.text)
        
        # Check common files
        for file in ['/hint.txt', '/password.txt', '/clue.txt', '/.env', '/config.json']:
            response = requests.get(url + file, timeout=5)
            if response.status_code == 200:
                print(f"\n[+] {file} found:")
                print(response.text[:500])
                
    except Exception as e:
        print(f"Error checking website: {e}")
