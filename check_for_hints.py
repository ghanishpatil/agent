#!/usr/bin/env python3
"""
Look for hidden hints in the challenge files
"""

import os

print("=== Checking for Hints ===\n")

# Check file sizes
files = [
    "challenge_CnK3cCB/encrypt.py",
    "challenge_CnK3cCB/flag_cipher.txt",
    "challenge_CnK3cCB/known_pair.txt",
    "challenge_CnK3cCB/diagram.png"
]

for f in files:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f"{f}: {size} bytes")

print()

# Check if there's any metadata or hidden data
print("Checking for steganography or hidden data in diagram.png...")

try:
    from PIL import Image
    import numpy as np
    
    img = Image.open("challenge_CnK3cCB/diagram.png")
    print(f"Image size: {img.size}")
    print(f"Image mode: {img.mode}")
    print(f"Image format: {img.format}")
    
    # Check LSB
    pixels = np.array(img)
    print(f"Pixel array shape: {pixels.shape}")
    
    # Extract LSBs
    if len(pixels.shape) == 3:
        lsbs = pixels[:, :, :] & 1
        print(f"LSB values (first 100): {lsbs.flatten()[:100]}")
    
except ImportError:
    print("PIL not available, skipping image analysis")
except Exception as e:
    print(f"Error analyzing image: {e}")

print()

# Check the plaintext and ciphertext for patterns
known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")

print("Analyzing known plaintext/ciphertext...")
print(f"PT: {known_pt.hex()}")
print(f"CT: {known_ct.hex()}")
print()

# Check if PT or CT contain ASCII text
print("PT as ASCII (errors ignored):", known_pt.decode('latin-1'))
print("CT as ASCII (errors ignored):", known_ct.decode('latin-1'))
print()

# Check for patterns in hex
print("Looking for patterns in hex...")
pt_hex = known_pt.hex()
ct_hex = known_ct.hex()

# Check for repeated bytes
from collections import Counter
pt_counts = Counter(known_pt)
ct_counts = Counter(known_ct)

print(f"PT byte frequency: {pt_counts.most_common(5)}")
print(f"CT byte frequency: {ct_counts.most_common(5)}")
print()

# Check if the challenge name gives hints
print("Challenge name: CnK3cCB")
print("Possible interpretations:")
print("  - C and K (Cipher and Key?)")
print("  - 3cCB might be hex: 0x3cCB = 15563")
print("  - Could be base64 encoded?")

import base64
try:
    decoded = base64.b64decode("CnK3cCB")
    print(f"  - Base64 decode: {decoded}")
except:
    print("  - Not valid base64")

print()

# Check if there's a relationship between PT and CT indices
print("Checking positional relationships...")
for i in range(len(known_pt)):
    diff = (known_ct[i] - known_pt[i]) % 256
    print(f"Position {i:2d}: PT={known_pt[i]:3d} (0x{known_pt[i]:02x}), CT={known_ct[i]:3d} (0x{known_ct[i]:02x}), diff={diff:3d} (0x{diff:02x})")
