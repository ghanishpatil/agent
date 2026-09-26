#!/usr/bin/env python3
"""
Analyze the challenge with the robots.txt hint
"""

import requests
from PIL import Image
import numpy as np

TARGET_URL = "http://138.199.163.92:12669/"

# The hint from robots.txt
hint = "q355q636678723p4"

print("="*60)
print("ANALYZING WITH HINT: " + hint)
print("="*60)

# Try the hint as a parameter to svg.php
print("\n[*] Trying hint as parameter to /svg.php...")
params_to_try = [
    {'key': hint},
    {'secret': hint},
    {'token': hint},
    {'q': hint},
    {'code': hint},
    {'pass': hint},
]

for params in params_to_try:
    resp = requests.get(TARGET_URL + "svg.php", params=params)
    print(f"  {params}: {len(resp.text)} bytes")
    if 'Kaal{' in resp.text:
        print(f"  [!] FLAG FOUND: {resp.text}")

# Try POST
print("\n[*] Trying POST to /svg.php...")
resp = requests.post(TARGET_URL + "svg.php", data={'key': hint})
print(f"  POST with key: {len(resp.text)} bytes")
if 'Kaal{' in resp.text:
    print(f"  [!] FLAG FOUND: {resp.text}")

# Try as path
print("\n[*] Trying hint as path...")
resp = requests.get(TARGET_URL + hint)
print(f"  /{hint}: {resp.status_code}")
if resp.status_code == 200:
    print(f"  Content: {resp.text[:200]}")

# Analyze the banner image
print("\n[*] Analyzing lore/banner.png...")
try:
    img = Image.open('lore_banner.png')
    print(f"  Size: {img.size}")
    print(f"  Mode: {img.mode}")
    
    # Check for LSB steganography
    pixels = np.array(img)
    print(f"  Shape: {pixels.shape}")
    
    # Extract LSBs
    if len(pixels.shape) == 3:
        lsb_data = pixels[:, :, :3] & 1
        # Try to read as binary
        flat = lsb_data.flatten()
        binary_str = ''.join(str(b) for b in flat[:800])
        print(f"  LSB binary (first 100 bits): {binary_str[:100]}")
        
        # Try to decode as ASCII
        if len(binary_str) >= 8:
            text = ''
            for i in range(0, min(len(binary_str), 800), 8):
                byte = binary_str[i:i+8]
                if len(byte) == 8:
                    val = int(byte, 2)
                    if 32 <= val <= 126:
                        text += chr(val)
                    else:
                        text += '.'
            print(f"  LSB text: {text[:100]}")
            
            if 'Kaal{' in text:
                print(f"\n[!] FLAG IN IMAGE: {text}")
except Exception as e:
    print(f"  Error: {e}")

# Check if hint is encoded
print("\n[*] Analyzing hint string...")
print(f"  Hint: {hint}")
print(f"  Length: {len(hint)}")

# Try different interpretations
# Could be: q=355, q=636, 678723, p=4
parts = hint.replace('q', ' q').replace('p', ' p').split()
print(f"  Parts: {parts}")

# Maybe it's coordinates or indices
import re
numbers = re.findall(r'\d+', hint)
print(f"  Numbers: {numbers}")

# Try as SVG parameter
print("\n[*] Trying numbers as SVG parameters...")
for num in numbers:
    resp = requests.get(TARGET_URL + f"svg.php?k={num}")
    if len(resp.text) != 107039:  # Different from default
        print(f"  k={num}: {len(resp.text)} bytes (DIFFERENT!)")
        if 'Kaal{' in resp.text:
            print(f"  [!] FLAG: {resp.text}")

print("\n" + "="*60)
