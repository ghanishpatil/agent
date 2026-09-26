#!/usr/bin/env python3
"""
Ultimate attempt - maybe the password is simpler than we think
Let's try EVERYTHING including case variations and special patterns
"""

import hashlib
import itertools

target = "707b10ba2d8020957997e4127c99147091087a71"

print("ULTIMATE HASH CRACKING ATTEMPT")
print("="*70)

# Maybe it's a simple word we haven't tried with exact casing
words = [
    'world', 'World', 'WORLD',
    'admin', 'Admin', 'ADMIN',
    'password', 'Password', 'PASSWORD',
    'betrayal', 'Betrayal', 'BETRAYAL',
    'employee', 'Employee', 'EMPLOYEE',
    'stolen', 'Stolen', 'STOLEN',
    'data', 'Data', 'DATA',
    'disk', 'Disk', 'DISK',
    'hidden', 'Hidden', 'HIDDEN',
    'location', 'Location', 'LOCATION',
    'storage', 'Storage', 'STORAGE',
    'device', 'Device', 'DEVICE',
    'recover', 'Recover', 'RECOVER',
    'information', 'Information', 'INFORMATION',
    'confidential', 'Confidential', 'CONFIDENTIAL',
    'trust', 'Trust', 'TRUST',
    'external', 'External', 'EXTERNAL',
    'hard', 'Hard', 'HARD',
    'clue', 'Clue', 'CLUE',
    'encrypted', 'Encrypted', 'ENCRYPTED',
    'text', 'Text', 'TEXT',
    'website', 'Website', 'WEBSITE',
    'link', 'Link', 'LINK',
    'identify', 'Identify', 'IDENTIFY',
    'retrieve', 'Retrieve', 'RETRIEVE',
    'copy', 'Copy', 'COPY',
    'present', 'Present', 'PRESENT',
    'attempt', 'Attempt', 'ATTEMPT',
    'method', 'Method', 'METHOD',
    'discover', 'Discover', 'DISCOVER',
    'later', 'Later', 'LATER',
    'difficult', 'Difficult', 'DIFFICULT',
    'unfortunately', 'Unfortunately', 'UNFORTUNATELY',
]

for w in words:
    if hashlib.sha1(w.encode()).hexdigest() == target:
        print(f"FOUND: {w}")
        exit(0)

# Try 5-letter lowercase words
print("Trying 5-letter words...")
import string
for combo in itertools.product(string.ascii_lowercase, repeat=5):
    pwd = ''.join(combo)
    if hashlib.sha1(pwd.encode()).hexdigest() == target:
        print(f"FOUND: {pwd}")
        exit(0)

print("Not found")
