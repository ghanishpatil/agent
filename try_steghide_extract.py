#!/usr/bin/env python3
"""
Try to extract hidden data using various methods
Maybe there's a password-protected steganography
"""

import subprocess
import os

# The password we found might be useful
password = "2157869541235478521545895"

for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    output = f'{stone}_extracted.txt'
    
    print(f"\n{'='*70}")
    print(f"Trying to extract from: {stone}")
    print('='*70)
    
    # Try steghide (if available)
    try:
        result = subprocess.run(
            ['steghide', 'extract', '-sf', filename, '-xf', output, '-p', password],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"SUCCESS! Extracted to {output}")
            with open(output, 'r') as f:
                print(f"Content: {f.read()}")
        else:
            print(f"steghide failed: {result.stderr}")
    except FileNotFoundError:
        print("steghide not installed")
    except Exception as e:
        print(f"Error: {e}")
    
    # Try without password
    try:
        result = subprocess.run(
            ['steghide', 'extract', '-sf', filename, '-xf', output, '-p', ''],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"SUCCESS (no password)! Extracted to {output}")
            with open(output, 'r') as f:
                print(f"Content: {f.read()}")
    except:
        pass

# Maybe the challenge expects us to get the RSA params from the platform
print("\n" + "="*70)
print("ALTERNATIVE: Check challenge platform for RSA parameters")
print("="*70)
print("Typically, CTF challenges provide RSA parameters in:")
print("1. Challenge description")
print("2. A separate .txt file")
print("3. As output from a server/service")
print("\nThe audio files might just be a distraction or container")
print("The actual n and c values should be provided separately")
