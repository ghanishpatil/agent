#!/usr/bin/env python3
"""
Try passwords VERY specific to this CTF challenge
Since it's not in rockyou, it must be custom
"""

import hashlib

target = "707b10ba2d8020957997e4127c99147091087a71"

print("="*70)
print("CTF-SPECIFIC PASSWORD CRACKING")
print("="*70)

# Challenge details:
# - Author: Le0 / Haardik Bhagtani
# - Challenge: Betrayal
# - Website: login-page-auqw.vercel.app
# - Encrypted token provided
# - Comment in HTML: KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8=
# - Username: hello

# Try VERY specific passwords
specific_passwords = [
    # From the URL
    'auqw', 'AUQW', 'Auqw',
    'login-page-auqw', 'auqw-login', 'vercel-auqw',
    
    # From author names
    'Le0', 'le0', 'LE0', 'Leo', 'leo', 'LEO',
    'Haardik', 'haardik', 'HAARDIK',
    'Bhagtani', 'bhagtani', 'BHAGTANI',
    'HaardikBhagtani', 'haardikbhagtani',
    'Le0Haardik', 'le0haardik',
    
    # Challenge name variations
    'Betrayal', 'betrayal', 'BETRAYAL',
    'BetrayalCTF', 'betrayalctf',
    'KaalBetray', 'kaalbetrayal',
    
    # From the story
    'employee', 'Employee', 'EMPLOYEE',
    'stolen', 'Stolen', 'STOLEN',
    'harddisk', 'HardDisk', 'HARDDISK',
    'harddisks', 'HardDisks',
    'hidden', 'Hidden', 'HIDDEN',
    'location', 'Location', 'LOCATION',
    'kolkata', 'Kolkata', 'KOLKATA',
    
    # Combinations
    'hello_world', 'hello-world', 'helloworld',
    'hello@world', 'hello!world', 'hello#world',
    'world!', 'world@', 'world#',
    'World!', 'World@', 'World#',
    
    # From the encrypted token (first/last parts)
    'SpSkjxA0', 'xoB7', 'SpSk',
    
    # From the comment
    'KRgda0', 'jlu6D', 'KRgda0-jlu6D',
    
    # CTF platform specific
    'Kaalchakra', 'kaalchakra', 'KAALCHAKRA',
    'KaalCTF', 'kaalctf', 'KAALCTF',
    'Kaal2024', 'Kaal2025', 'Kaal2026',
    'kaal2024', 'kaal2025', 'kaal2026',
    
    # Vercel specific
    'vercel', 'Vercel', 'VERCEL',
    'vercel123', 'Vercel123',
    
    # Login page specific
    'loginpage', 'LoginPage', 'LOGINPAGE',
    'authorized', 'Authorized', 'AUTHORIZED',
    'admin', 'Admin', 'ADMIN',
    'welcome', 'Welcome', 'WELCOME',
    
    # Points/difficulty
    '500', 'hard', 'Hard', 'HARD',
    'miscellaneous', 'Miscellaneous', 'MISCELLANEOUS',
    
    # Opposite/related to hello
    'goodbye', 'Goodbye', 'GOODBYE',
    'bye', 'Bye', 'BYE',
    'world', 'World', 'WORLD',
    'there', 'There', 'THERE',
    
    # Common CTF patterns with hello
    'hello1', 'hello2', 'hello3', 'hello123', 'hello321',
    'Hello1', 'Hello2', 'Hello3', 'Hello123', 'Hello321',
    'HELLO1', 'HELLO2', 'HELLO3', 'HELLO123', 'HELLO321',
    'hello!', 'hello@', 'hello#', 'hello$', 'hello%',
    'Hello!', 'Hello@', 'Hello#', 'Hello$', 'Hello%',
    
    # Maybe it's the hash itself or part of it
    '707b10ba', '707b10ba2d8020957997e4127c99147091087a71',
    
    # Maybe it's related to the username hash
    'aaf4c61d', 'aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d',
    
    # Try simple transformations
    'h3ll0', 'H3LL0', 'h3110', 'H3110',
    'w0rld', 'W0RLD', 'w0r1d', 'W0R1D',
    
    # Try dates
    '20240328', '20250328', '20260328', '20260329',
    '28032024', '28032025', '28032026', '29032026',
    
    # Try common CTF passwords
    'flag', 'Flag', 'FLAG',
    'flag{', 'Flag{', 'FLAG{',
    'Kaal{', 'kaal{', 'KAAL{',
    
    # Try the challenge description words
    'trust', 'Trust', 'TRUST',
    'confidential', 'Confidential', 'CONFIDENTIAL',
    'recover', 'Recover', 'RECOVER',
    'information', 'Information', 'INFORMATION',
    
    # Try combinations with numbers
    'betrayal123', 'Betrayal123', 'BETRAYAL123',
    'employee123', 'Employee123', 'EMPLOYEE123',
    'stolen123', 'Stolen123', 'STOLEN123',
    'le0123', 'Le0123', 'LE0123',
    'haardik123', 'Haardik123', 'HAARDIK123',
    
    # Try with special characters
    'betrayal!', 'Betrayal!', 'BETRAYAL!',
    'employee!', 'Employee!', 'EMPLOYEE!',
    'stolen!', 'Stolen!', 'STOLEN!',
    
    # Try phrases
    'hello there', 'Hello There', 'HELLO THERE',
    'hello_there', 'Hello_There', 'HELLO_THERE',
    'hellothere', 'HelloThere', 'HELLOTHERE',
]

print(f"\nTrying {len(specific_passwords)} CTF-specific passwords...")

for pwd in specific_passwords:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == target:
        print(f"\n*** PASSWORD FOUND: {pwd} ***")
        print(f"Hash: {h}")
        
        with open('BETRAYAL_PASSWORD.txt', 'w') as f:
            f.write(f"Password: {pwd}\n")
            f.write(f"Hash: {h}\n")
        
        exit(0)

print("\n✗ Password not found in CTF-specific list")
print("\nThe password might be:")
print("  - A random string generated for this challenge")
print("  - Hidden in the challenge page or description")
print("  - Requires solving another part first")
print("  - In the encrypted token itself (needs decryption)")
