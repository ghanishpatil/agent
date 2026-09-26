#!/usr/bin/env python3
import subprocess
import re

exe = r".\challenge_mystery\crackme.exe"

# Extract strings
with open(exe, 'rb') as f:
    data = f.read()

text = data.decode('latin-1', errors='ignore')

# Find interesting strings
print("[*] Searching for strings...")
for pattern in [r'Kaal\{[^}]+\}', r'flag', r'key', r'password', r'correct', r'wrong']:
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        print(f"  {pattern}: {set(matches)}")

# Look for encoded data
print("\n[*] Looking for base64/hex patterns...")
b64_pattern = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', text)
if b64_pattern:
    print(f"  Found {len(b64_pattern)} base64-like strings")
    for s in b64_pattern[:5]:
        print(f"    {s[:50]}")

# Try common inputs
print("\n[*] Testing common inputs...")
for test in ['admin', 'password', '1234', 'key', 'flag', 'Kaal']:
    try:
        result = subprocess.run([exe], input=test.encode(), capture_output=True, timeout=2)
        output = result.stdout.decode(errors='ignore')
        if 'Kaal{' in output or 'correct' in output.lower() or 'success' in output.lower():
            print(f"  [{test}] -> {output[:100]}")
    except:
        pass
