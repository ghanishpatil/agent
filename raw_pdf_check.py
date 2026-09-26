#!/usr/bin/env python3

# Read raw PDF bytes to look for any hints
with open("Cases/Flag_protected.pdf", "rb") as f:
    data = f.read()
    
# Convert to string (ignore errors)
text = data.decode('latin-1')

# Look for any readable strings
import re

# Find any BPCTF patterns (might be visible in raw)
flags = re.findall(r'BPCTF\{[^}]+\}', text)
if flags:
    print("FOUND FLAG IN RAW PDF:")
    for flag in flags:
        print(flag)
    exit(0)

# Look for password hints
hints = re.findall(r'password[:\s]+([a-zA-Z0-9_\-]+)', text, re.IGNORECASE)
if hints:
    print("Found password hints:", hints)

# Look for any readable text
words = re.findall(r'[A-Za-z]{4,}', text)
unique_words = list(set(words))[:50]
print("Readable words in PDF:")
for word in sorted(unique_words):
    print(f"  {word}")

# Try these as passwords
import pikepdf
print("\nTrying found words as passwords...")
for word in unique_words:
    try:
        with pikepdf.open("Cases/Flag_protected.pdf", password=word) as pdf:
            print(f"\n*** FOUND: {word} ***")
            exit(0)
    except:
        pass

print("\nNo password found in raw PDF")
