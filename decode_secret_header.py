#!/usr/bin/env python3
"""
Decode the X-Secret and X-Prefix headers
"""

import re

prefix = "laak_560c83ed"
secret = "38h4vg6s45ch1lr19x4pe18s55r2kh1lx5331mh1mc5656w0"

print("="*60)
print("Decoding Secret Headers")
print("="*60)

print(f"\nX-Prefix: {prefix}")
print(f"X-Secret: {secret}")

# The prefix is "laak" reversed = "kaal"!
print(f"\nPrefix reversed: {prefix[:4][::-1]}")

# The secret looks like it might be encoded
# Let's try different decodings

# 1. Check if it's hex
try:
    decoded_hex = bytes.fromhex(secret).decode('utf-8', errors='ignore')
    print(f"\nHex decode: {decoded_hex}")
except:
    print("\nNot valid hex")

# 2. Check if numbers spell something
# Extract all numbers
numbers = ''.join(c for c in secret if c.isdigit())
print(f"\nNumbers only: {numbers}")

# 3. Extract all letters
letters = ''.join(c for c in secret if c.isalpha())
print(f"Letters only: {letters}")

# 4. Maybe it's a substitution cipher?
# The secret has a pattern: numbers and letters mixed

# 5. Try reading it as coordinates or indices
# Maybe the numbers are indices into the grid?

# 6. Check if it's base64-like
import base64
try:
    decoded_b64 = base64.b64decode(secret).decode('utf-8', errors='ignore')
    print(f"\nBase64 decode: {decoded_b64}")
except:
    print("\nNot valid base64")

# 7. Maybe the secret IS the flag or contains it?
if 'kaal{' in secret.lower():
    print(f"\n[!!!] FLAG IN SECRET!")

# 8. Try ROT13 or Caesar cipher
def caesar_decrypt(text, shift):
    result = []
    for char in text:
        if char.isalpha():
            if char.islower():
                result.append(chr((ord(char) - ord('a') - shift) % 26 + ord('a')))
            else:
                result.append(chr((ord(char) - ord('A') - shift) % 26 + ord('A')))
        else:
            result.append(char)
    return ''.join(result)

print("\n[*] Trying Caesar shifts...")
for shift in range(1, 26):
    decoded = caesar_decrypt(secret, shift)
    if 'kaal' in decoded.lower() or 'flag' in decoded.lower():
        print(f"  Shift {shift}: {decoded}")

# 9. Maybe we need to use this secret with the grid?
print("\n[*] The secret might be:")
print("  - A key to decode the bonus grid")
print("  - Coordinates to read from the grid")
print("  - Or indices into the grid letters")

# 10. Try using the numbers as grid coordinates
print("\n[*] Extracting number pairs as potential coordinates...")
nums = [c for c in secret if c.isdigit()]
if len(nums) >= 2:
    pairs = [(nums[i], nums[i+1]) for i in range(0, len(nums)-1, 2)]
    print(f"  Coordinate pairs: {pairs[:10]}")

# 11. The grid from earlier - let me try to use the secret as indices
grid_letters = "EAUIDHONISOARYOBTSWITCMPUMPKINRSOZMRTGHQSTIRQAUNIED"

print(f"\n[*] Grid letters: {grid_letters}")
print(f"[*] Trying to use secret as indices...")

# Extract numbers and use as indices
try:
    indices = [int(c) for c in secret if c.isdigit()]
    decoded_from_grid = ''.join(grid_letters[i % len(grid_letters)] for i in indices)
    print(f"  Decoded: {decoded_from_grid}")
    
    if 'kaal' in decoded_from_grid.lower():
        print(f"\n[!!!] FOUND KAAL IN DECODED TEXT!")
except Exception as e:
    print(f"  Error: {e}")
