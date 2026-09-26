#!/usr/bin/env python3
"""Deep analysis of greetings2 bytecode"""

import re

pyc_file = r".\greetings_extracted\greetings.pyc"

with open(pyc_file, 'rb') as f:
    data = f.read()

# Skip Python 3.14 header (16 bytes)
bytecode = data[16:]

print("=" * 60)
print("DEEP BYTECODE ANALYSIS")
print("=" * 60)

# Extract all strings more carefully
print("\n[*] Extracting all strings:")
text = data.decode('latin-1', errors='ignore')

# Find all sequences between quotes or null bytes
strings = []
current = []
for i, byte in enumerate(data):
    if 32 <= byte <= 126 and byte not in [34, 39]:  # printable, not quotes
        current.append(chr(byte))
    else:
        if len(current) >= 3:
            s = ''.join(current)
            strings.append(s)
        current = []

# Print unique strings
unique_strings = sorted(set(strings), key=len, reverse=True)
for s in unique_strings[:30]:
    if len(s) > 5:
        print(f"    {s}")

# Look for the exact code structure
print("\n[*] Looking for code patterns...")
if b'dumps' in data:
    print("    Found: pickle.dumps")
if b'loads' in data:
    print("    Found: pickle.loads")
if b'post' in data:
    print("    Found: requests.post")
if b'json' in data:
    print("    Found: json module")

# Extract the URL more carefully
url_match = re.search(rb'http://[^\x00\x01-\x1f]+', data)
if url_match:
    url = url_match.group(0).decode('latin-1')
    print(f"\n[*] Extracted URL: {url}")

# Look for hex/input patterns
if b'hex' in data:
    print("\n[*] Found 'hex' - likely uses .hex() method")
if b'input' in data:
    print("[*] Found 'input' - takes user input")

print("\n" + "=" * 60)
