#!/usr/bin/env python3
"""Analyze greetings2 binary"""

import re
import os

pyc_file = r".\greetings2\greetings_extracted\greetings.pyc"

print("=" * 60)
print("GREETINGS 2 ANALYSIS")
print("=" * 60)

if not os.path.exists(pyc_file):
    print(f"[-] File not found: {pyc_file}")
    exit(1)

with open(pyc_file, 'rb') as f:
    data = f.read()
    
print(f"\n[*] File size: {len(data)} bytes")

# Convert to string
text = data.decode('latin-1', errors='ignore')

# Search for Kaal{ pattern
print("\n[*] Searching for flag pattern...")
matches = re.findall(r'Kaal\{[^}]+\}', text)

if matches:
    print(f"\n[+] FOUND {len(matches)} FLAG(S):")
    for match in matches:
        print(f"    {match}")
else:
    print("[-] No direct flag found")
    
# Look for interesting strings
print("\n[*] Interesting strings:")
interesting = ['http', 'api', 'flag', 'password', 'key', 'secret', 'token']
for keyword in interesting:
    if keyword in text.lower():
        # Find context around keyword
        idx = text.lower().find(keyword)
        start = max(0, idx - 50)
        end = min(len(text), idx + 100)
        context = text[start:end].replace('\n', ' ').replace('\r', '')
        # Clean up non-printable
        context = ''.join(c if 32 <= ord(c) <= 126 else '?' for c in context)
        print(f"  {keyword}: ...{context}...")

# Extract all readable strings
print("\n[*] All readable strings (>10 chars):")
current = []
for byte in data:
    if 32 <= byte <= 126:
        current.append(chr(byte))
    else:
        if len(current) >= 10:
            s = ''.join(current)
            if any(k in s.lower() for k in ['http', 'api', 'kaal', 'flag', 'password']):
                print(f"    {s}")
        current = []

print("\n" + "=" * 60)
