#!/usr/bin/env python3
"""
Brute force the password hash
Hash: 707b10ba2d8020957997e4127c99147091087a71
"""

import hashlib

target_hash = "707b10ba2d8020957997e4127c99147091087a71"

print("Brute forcing password hash...")

# Try common passwords and variations
wordlist = [
    # Common passwords
    'password', 'admin', '123456', '12345678', 'qwerty', 'abc123',
    'monkey', 'letmein', 'trustno1', 'dragon', 'baseball', 'iloveyou',
    'master', 'sunshine', 'ashley', 'bailey', 'passw0rd', 'shadow',
    'superman', 'qazwsx', 'michael', 'football', 'welcome', 'jesus',
    
    # CTF related
    'flag', 'ctf', 'kaal', 'kaalchakra', 'betrayal', 'employee',
    'stolen', 'data', 'disk', 'storage', 'confidential', 'secret',
    'hidden', 'location', 'recover', 'encrypted', 'token',
    
    # Variations of "hello"
    'world', 'helloworld', 'hello123', 'hello!', 'hello@123',
    
    # Simple words
    'test', 'user', 'guest', 'root', 'toor', 'pass', 'login',
    
    # Numbers
    '1234', '12345', '123456', '1234567', '12345678', '123456789',
    '0000', '0123', '1111', '2222', '9999',
    
    # Common patterns
    'password1', 'password123', 'admin123', 'test123', 'user123',
    'qwerty123', 'abc123456', 'password!', 'admin!', 'P@ssw0rd',
    
    # Challenge specific
    'betrayal', 'employee', 'confidential', 'stolen', 'harddisk',
    'external', 'storage', 'devices', 'recover', 'information',
    'clue', 'website', 'link', 'encrypted', 'text', 'location'
]

for word in wordlist:
    h = hashlib.sha1(word.encode()).hexdigest()
    if h == target_hash:
        print(f"\n✓✓✓ PASSWORD FOUND: {word} ✓✓✓\n")
        break
else:
    print("Password not in wordlist, trying variations...")
    
    # Try with numbers appended
    for word in ['hello', 'world', 'admin', 'password', 'test']:
        for i in range(1000):
            candidate = f"{word}{i}"
            h = hashlib.sha1(candidate.encode()).hexdigest()
            if h == target_hash:
                print(f"\n✓✓✓ PASSWORD FOUND: {candidate} ✓✓✓\n")
                exit()
    
    # Try single words from rockyou-like list
    common_words = [
        'love', 'baby', 'angel', 'princess', 'sweet', 'lovely',
        'honey', 'forever', 'kiss', 'beautiful', 'sexy', 'hot',
        'crazy', 'cool', 'star', 'super', 'happy', 'smile',
        'dream', 'heart', 'life', 'friend', 'family', 'mother',
        'father', 'sister', 'brother', 'summer', 'winter', 'spring'
    ]
    
    for word in common_words:
        h = hashlib.sha1(word.encode()).hexdigest()
        if h == target_hash:
            print(f"\n✓✓✓ PASSWORD FOUND: {word} ✓✓✓\n")
            break
