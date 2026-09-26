#!/usr/bin/env python3
"""Decompile greetings.pyc"""

import subprocess
import sys
import os

pyc_file = r".\greetings_extracted\greetings.pyc"

print("=" * 60)
print("DECOMPILING GREETINGS.PYC")
print("=" * 60)

# Try uncompyle6
print("\n[*] Attempting decompilation with uncompyle6...")
try:
    result = subprocess.run([sys.executable, '-m', 'uncompyle6', pyc_file], 
                          capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"    uncompyle6 failed: {result.stderr}")
        
        # Try pycdc
        print("\n[*] Trying alternative: reading raw bytecode...")
        with open(pyc_file, 'rb') as f:
            data = f.read()
            # Skip magic number and timestamp (first 16 bytes in Python 3.14)
            print(f"    File size: {len(data)} bytes")
            print(f"    Magic: {data[:4].hex()}")
            
            # Try to extract strings
            print("\n[*] Extracting strings from bytecode:")
            text = data.decode('latin-1')
            for line in text.split('\n'):
                if 'Kaal{' in line or 'flag' in line.lower() or 'password' in line.lower():
                    print(f"    {line}")
            
except Exception as e:
    print(f"    Error: {e}")
    
    # Manual analysis
    print("\n[*] Manual bytecode analysis:")
    with open(pyc_file, 'rb') as f:
        data = f.read()
        text = data.decode('latin-1', errors='ignore')
        
        # Look for interesting strings
        import re
        strings = re.findall(r'[A-Za-z0-9_]{4,}', text)
        print("    Interesting strings:")
        for s in set(strings):
            if len(s) > 5:
                print(f"      {s}")

print("\n" + "=" * 60)
