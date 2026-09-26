#!/usr/bin/env python3
import re

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

# Extract all printable strings
strings = []
current = []
for byte in data:
    if 32 <= byte <= 126:
        current.append(chr(byte))
    else:
        if len(current) >= 4:
            strings.append(''.join(current))
        current = []

print("[*] Interesting strings:")
for s in strings:
    if any(k in s.lower() for k in ['kaal', 'flag', 'enter', 'key', 'correct', 'wrong', 'success']):
        print(f"  {s}")

# Look for XOR keys or encoded data
print("\n[*] Looking for hex patterns...")
hex_pattern = re.findall(rb'[0-9A-Fa-f]{32,}', data)
for h in hex_pattern[:10]:
    print(f"  {h[:50]}")

# Check for common crackme patterns
print("\n[*] Checking for validation logic...")
if b'strcmp' in data or b'memcmp' in data:
    print("  Found string comparison functions")
if b'xor' in data.lower():
    print("  Found XOR reference")
