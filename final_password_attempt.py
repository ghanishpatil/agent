#!/usr/bin/env python3
"""
Final attempt to crack the password
Let's try EVERYTHING including common passwords from rockyou-style lists
"""

import hashlib

target_hash = "707b10ba2d8020957997e4127c99147091087a71"

print("="*70)
print("FINAL PASSWORD CRACKING ATTEMPT")
print("="*70)

# Most common passwords from rockyou.txt
rockyou_top = [
    '123456', 'password', '12345678', 'qwerty', '123456789', '12345', '1234',
    '111111', '1234567', 'dragon', '123123', 'baseball', 'iloveyou', 'trustno1',
    '1234567890', 'sunshine', 'master', '123321', '666666', 'photoshop', '1111111',
    '7777777', '1q2w3e4r', '654321', '555555', 'lovely', '7777777', '888888',
    'princess', 'dragon', 'password1', '123qwe', 'zxcvbnm', '121212', 'bailey',
    'freedom', 'shadow', 'passw0rd', 'baseball', 'welcome', 'abc123', 'football',
    'monkey', 'letmein', '696969', 'shadow', 'master', '666666', 'qwertyuiop',
    'hottie', 'freedom', 'aa123456', 'qazwsx', 'ninja', 'azerty', 'loveme',
    'whatever', 'donald', 'batman', 'zaq1zaq1', 'qazwsx', 'password123',
    'Password', 'Password1', 'password!', 'qwerty123', 'qwerty1', 'Qwerty',
    'starwars', 'klaster', 'solo', 'hello', 'freedom', 'whatever', 'qazwsx',
    'trustno1', 'jordan', 'jennifer', 'hunter', 'buster', 'soccer', 'harley',
    'batman', 'andrew', 'tigger', 'sunshine', 'iloveyou', '2000', 'charlie',
    'robert', 'thomas', 'hockey', 'ranger', 'daniel', 'starwars', 'klaster',
    '112233', 'george', 'computer', 'michelle', 'jessica', 'pepper', '1111',
    'zxcvbn', '555555', '11111111', '131313', 'freedom', '777777', 'pass',
    'maggie', '159753', 'aaaaaa', 'ginger', 'princess', 'joshua', 'cheese',
    'amanda', 'summer', 'love', 'ashley', 'nicole', 'chelsea', 'biteme',
    'matthew', 'access', 'yankees', '987654321', 'dallas', 'austin', 'thunder',
    'taylor', 'matrix', 'mobilemail', 'mom', 'monitor', 'monitoring', 'montana',
    'moon', 'moscow'
]

print("\nTrying top rockyou passwords...")
for pwd in rockyou_top:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND: {pwd} ***")
        exit(0)

# Try with special characters
print("\nTrying with special characters...")
base_words = ['admin', 'password', 'hello', 'world', 'kaal', 'betrayal']
special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=']

for word in base_words:
    for char in special_chars:
        for pwd in [word + char, char + word, word + char + word]:
            h = hashlib.sha1(pwd.encode()).hexdigest()
            if h == target_hash:
                print(f"\n*** PASSWORD FOUND: {pwd} ***")
                exit(0)

# Try common patterns
print("\nTrying common patterns...")
patterns = []

# Pattern: word + number (1-100)
for word in ['admin', 'password', 'user', 'test', 'hello', 'world']:
    for i in range(1, 101):
        patterns.append(f"{word}{i}")
        patterns.append(f"{word}{i:02d}")
        patterns.append(f"{word}{i:03d}")

# Pattern: number + word
for word in ['admin', 'password', 'user', 'test']:
    for i in range(1, 101):
        patterns.append(f"{i}{word}")

# Pattern: word + year
for word in ['admin', 'password', 'user', 'test', 'hello']:
    for year in range(2015, 2027):
        patterns.append(f"{word}{year}")
        patterns.append(f"{year}{word}")

for pwd in patterns:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND: {pwd} ***")
        exit(0)

# Try keyboard patterns
print("\nTrying keyboard patterns...")
keyboard_patterns = [
    'qwerty', 'qwertyuiop', 'asdfgh', 'asdfghjkl', 'zxcvbn', 'zxcvbnm',
    'qazwsx', 'qazwsxedc', 'qweasd', 'qweasdzxc', '1qaz2wsx', '1q2w3e4r',
    '1q2w3e4r5t', 'zaq12wsx', 'zaq1xsw2', 'qwerasdf', 'qwerasdfzxcv'
]

for pwd in keyboard_patterns:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND: {pwd} ***")
        exit(0)

# Try names
print("\nTrying common names...")
names = [
    'john', 'mike', 'david', 'james', 'robert', 'michael', 'william', 'richard',
    'joseph', 'thomas', 'charles', 'daniel', 'matthew', 'anthony', 'donald',
    'mark', 'paul', 'steven', 'andrew', 'kenneth', 'joshua', 'kevin', 'brian',
    'george', 'edward', 'ronald', 'timothy', 'jason', 'jeffrey', 'ryan',
    'jacob', 'gary', 'nicholas', 'eric', 'jonathan', 'stephen', 'larry',
    'justin', 'scott', 'brandon', 'benjamin', 'samuel', 'raymond', 'gregory',
    'frank', 'alexander', 'patrick', 'jack', 'dennis', 'jerry', 'tyler',
    'aaron', 'jose', 'adam', 'henry', 'nathan', 'douglas', 'zachary', 'peter',
    'kyle', 'walter', 'ethan', 'jeremy', 'harold', 'keith', 'christian', 'roger',
    'noah', 'gerald', 'carl', 'terry', 'sean', 'austin', 'arthur', 'lawrence',
    'jesse', 'dylan', 'bryan', 'joe', 'jordan', 'billy', 'bruce', 'albert',
    'willie', 'gabriel', 'logan', 'alan', 'juan', 'wayne', 'roy', 'ralph',
    'randy', 'eugene', 'vincent', 'russell', 'elijah', 'louis', 'bobby', 'philip',
    'johnny'
]

for name in names:
    for pwd in [name, name.capitalize(), name.upper()]:
        h = hashlib.sha1(pwd.encode()).hexdigest()
        if h == target_hash:
            print(f"\n*** PASSWORD FOUND: {pwd} ***")
            exit(0)
    
    # Try with numbers
    for i in [1, 12, 123, 1234, 12345]:
        pwd = name + str(i)
        h = hashlib.sha1(pwd.encode()).hexdigest()
        if h == target_hash:
            print(f"\n*** PASSWORD FOUND: {pwd} ***")
            exit(0)

# Try dictionary words
print("\nTrying dictionary words...")
dictionary = [
    'apple', 'banana', 'orange', 'grape', 'melon', 'cherry', 'peach', 'pear',
    'computer', 'laptop', 'desktop', 'keyboard', 'mouse', 'monitor', 'printer',
    'internet', 'network', 'server', 'database', 'software', 'hardware',
    'security', 'firewall', 'antivirus', 'malware', 'virus', 'trojan', 'worm',
    'hacker', 'cracker', 'exploit', 'vulnerability', 'patch', 'update',
    'system', 'windows', 'linux', 'ubuntu', 'debian', 'fedora', 'centos',
    'android', 'iphone', 'samsung', 'google', 'facebook', 'twitter', 'instagram',
    'youtube', 'netflix', 'amazon', 'microsoft', 'apple', 'oracle', 'cisco',
    'secret', 'private', 'confidential', 'classified', 'restricted', 'sensitive',
    'important', 'critical', 'urgent', 'emergency', 'warning', 'danger', 'alert',
    'access', 'login', 'logout', 'signin', 'signout', 'register', 'signup',
    'account', 'profile', 'settings', 'preferences', 'options', 'configuration',
    'welcome', 'goodbye', 'thanks', 'please', 'sorry', 'excuse', 'pardon'
]

for word in dictionary:
    h = hashlib.sha1(word.encode()).hexdigest()
    if h == target_hash:
        print(f"\n*** PASSWORD FOUND: {word} ***")
        exit(0)

print("\nPassword not found in common lists.")
print("\nThe password might be:")
print("  1. In a larger wordlist (full rockyou.txt)")
print("  2. A random string")
print("  3. Something specific to the challenge context")
print("\nTry online hash crackers or download rockyou.txt")
