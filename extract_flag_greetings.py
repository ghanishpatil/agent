#!/usr/bin/env python3
"""Extract flag from greetings.pyc"""

import re

pyc_file = r".\greetings_extracted\greetings.pyc"

print("=" * 60)
print("FLAG EXTRACTION FROM GREETINGS.PYC")
print("=" * 60)

with open(pyc_file, 'rb') as f:
    data = f.read()
    
# Convert to string
text = data.decode('latin-1', errors='ignore')

# Search for Kaal{ pattern
matches = re.findall(r'Kaal\{[^}]+\}', text)

if matches:
    print("\n[+] FLAG FOUND!")
    for match in matches:
        print(f"\n    {match}")
else:
    print("\n[-] No flag found with regex, searching manually...")
    if 'Kaal{' in text:
        idx = text.index('Kaal{')
        end_idx = text.find('}', idx)
        if end_idx != -1:
            flag = text[idx:end_idx+1]
            print(f"\n[+] FLAG FOUND: {flag}")

print("\n" + "=" * 60)
