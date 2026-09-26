#!/usr/bin/env python3
"""Analyze greetings2 - check if it's different from greetings1"""

import re
import os

pyc_file = r".\greetings_extracted\greetings.pyc"

print("=" * 60)
print("GREETINGS 2 BYTECODE ANALYSIS")
print("=" * 60)

with open(pyc_file, 'rb') as f:
    data = f.read()
    
print(f"\n[*] File size: {len(data)} bytes")

# Convert to string
text = data.decode('latin-1', errors='ignore')

# Search for URLs
print("\n[*] Searching for URLs...")
urls = re.findall(r'https?://[^\s\'"<>]+', text)
if urls:
    for url in urls:
        print(f"    {url}")

# Search for Kaal{ pattern
print("\n[*] Searching for flag patterns...")
matches = re.findall(r'Kaal\{[^}]+\}', text)
if matches:
    print(f"\n[+] FOUND {len(matches)} FLAG(S):")
    for match in matches:
        print(f"    {match}")

# Look for API endpoints
print("\n[*] Looking for API-related strings...")
if '/api' in text:
    idx = text.find('/api')
    context = text[max(0, idx-20):min(len(text), idx+100)]
    print(f"    Found /api context: {repr(context[:100])}")

# Extract function/variable names
print("\n[*] Extracting identifiers...")
identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]{3,}\b', text)
interesting_ids = [id for id in set(identifiers) if any(k in id.lower() for k in ['flag', 'key', 'secret', 'password', 'token', 'api', 'url'])]
if interesting_ids:
    print("    Interesting identifiers:")
    for id in sorted(interesting_ids)[:20]:
        print(f"      {id}")

print("\n" + "=" * 60)
