#!/usr/bin/env python3
"""
Final attempt - maybe the password is related to the challenge theme
"betrayal", "employee", "stolen", "confidential", "data", "disk", "storage"
"""

import hashlib
import requests

target_hash = "707b10ba2d8020957997e4127c99147091087a71"

# Challenge-specific wordlist
wordlist = [
    # From challenge description
    'betrayed', 'trust', 'stolen', 'confidential', 'data', 'recover',
    'systems', 'external', 'storage', 'devices', 'hidden', 'harddisk',
    'hard disk', 'harddisks', 'hard disks', 'clue', 'encrypted', 'text',
    'website', 'link', 'location', 'information', 'employee', 'employees',
    
    # Common variations
    'world', 'helloworld', 'hello123', 'admin', 'password', 'secret',
    
    # CTF related
    'kaalchakra', 'kaal', 'ctf', 'flag',
    
    # Author name
    'le0', 'leo', 'Le0',
    
    # Vercel/website related
    'vercel', 'login', 'page', 'auth', 'authorized',
    
    # Simple words that might relate
    'disk', 'drive', 'usb', 'flash', 'memory', 'card', 'sd',
    
    # Numbers
    '500', '2024', '2025', '123', '1234', '12345'
]

print("Testing challenge-specific passwords...")

for word in wordlist:
    h = hashlib.sha1(word.encode()).hexdigest()
    if h == target_hash:
        print(f"\n✓✓✓ PASSWORD FOUND: {word} ✓✓✓\n")
        
        # Now try to login
        print("Attempting to access protected content...")
        
        url = "https://login-page-auqw.vercel.app/"
        
        # Try different methods to submit credentials
        # Method 1: Check if there's a /dashboard or /admin page
        for endpoint in ['/dashboard', '/admin', '/flag', '/data', '/disk', '/location']:
            try:
                # Try with basic auth
                r = requests.get(url + endpoint, auth=('hello', word), timeout=5)
                if r.status_code == 200:
                    print(f"  {endpoint}: {r.status_code}")
                    if 'Kaal{' in r.text:
                        print(f"  *** FLAG FOUND: ***")
                        import re
                        flags = re.findall(r'Kaal\{[^}]+\}', r.text)
                        for flag in flags:
                            print(f"  {flag}")
            except:
                pass
        
        break
else:
    print("Password not found in wordlist")
    
    # Try online hash cracker
    print("\nTrying online hash lookup...")
    
    # CrackStation API (if available)
    try:
        r = requests.get(f"https://md5decrypt.net/en/Sha1/#{target_hash}", timeout=10)
        if 'Decrypted' in r.text or 'Result' in r.text:
            print(f"Check: https://md5decrypt.net/en/Sha1/#{target_hash}")
    except:
        pass
    
    print(f"\nManual lookup needed:")
    print(f"Hash: {target_hash}")
    print(f"Try: https://crackstation.net/")
    print(f"Try: https://hashes.com/en/decrypt/hash")

print("\nDone")
