#!/usr/bin/env python3
"""Analyze the greetings binary for reverse engineering challenge"""

import subprocess
import os

binary_path = r".\greetings\greetings"

print("=" * 60)
print("GREETINGS BINARY ANALYSIS")
print("=" * 60)

# Check if it's executable
print("\n[*] File info:")
if os.path.exists(binary_path):
    size = os.path.getsize(binary_path)
    print(f"    Size: {size} bytes")
else:
    print("    File not found!")
    exit(1)

# Try to extract strings
print("\n[*] Extracting strings from binary...")
try:
    result = subprocess.run(['strings', binary_path], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        strings = result.stdout.strip().split('\n')
        print(f"    Found {len(strings)} strings")
        print("\n[*] Interesting strings:")
        for s in strings:
            if len(s) > 3:  # Filter short strings
                print(f"    {s}")
    else:
        print("    strings command not available, trying manual extraction...")
        with open(binary_path, 'rb') as f:
            data = f.read()
            # Simple string extraction
            current = []
            for byte in data:
                if 32 <= byte <= 126:  # Printable ASCII
                    current.append(chr(byte))
                else:
                    if len(current) >= 4:
                        print(f"    {''.join(current)}")
                    current = []
except Exception as e:
    print(f"    Error: {e}")
    # Manual extraction
    print("\n[*] Manual string extraction:")
    with open(binary_path, 'rb') as f:
        data = f.read()
        current = []
        for byte in data:
            if 32 <= byte <= 126:
                current.append(chr(byte))
            else:
                if len(current) >= 4:
                    print(f"    {''.join(current)}")
                current = []

print("\n[*] Searching for flag patterns (Kaal{...}):")
with open(binary_path, 'rb') as f:
    data = f.read()
    text = data.decode('latin-1')
    
    # Search for Kaal{ pattern
    if 'Kaal{' in text:
        idx = text.index('Kaal{')
        # Extract potential flag
        end_idx = text.find('}', idx)
        if end_idx != -1:
            flag = text[idx:end_idx+1]
            print(f"    FOUND FLAG: {flag}")
    else:
        print("    No direct flag found in binary")

print("\n" + "=" * 60)
