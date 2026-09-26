#!/usr/bin/env python3
"""
Ultimate attempt to find the flag
"""

import re
import itertools

# All the data we have
prefix = "laak"  # reversed = kaal
secret = "38h4vg6s45ch1lr19x4pe18s55r2kh1lx5331mh1mc5656w0"

# Grid data
grid_rows = [
    "4EAUIDHON8",
    "3ISOARY7O7",
    "4BTSWITCM2",
    "56PUMPKIN1",
    "8RSOZMRT10",
    "89GHQST893",
    "3I3286RQ11",
    "HAUNIED488",
]

print("="*60)
print("ULTIMATE FLAG FINDER")
print("="*60)

# 1. Check if flag is directly in any data
all_text = prefix + secret + ''.join(grid_rows)
print(f"\n[*] Checking all text for flag pattern...")

if re.search(r'kaal\{[^}]+\}', all_text, re.IGNORECASE):
    flag = re.search(r'kaal\{[^}]+\}', all_text, re.IGNORECASE)
    print(f"[!!!] FLAG: {flag.group(0)}")

# 2. Try building flag from grid words
print("\n[*] Words found in grid:")
words = ["HAUNIED", "PUMPKIN"]
print(f"  {words}")

# Maybe HAUNIED is an anagram?
from itertools import permutations
haunied_perms = [''.join(p) for p in permutations("HAUNIED")]
for perm in haunied_perms[:20]:
    if "HAUNTED" in perm or "UNTIED" in perm:
        print(f"  Anagram: {perm}")

# 3. Try using secret as a key
print("\n[*] Using secret to extract from grid...")

# Extract only letters from secret
secret_letters = ''.join(c for c in secret if c.isalpha())
print(f"  Secret letters: {secret_letters}")

# Extract only numbers
secret_numbers = ''.join(c for c in secret if c.isdigit())
print(f"  Secret numbers: {secret_numbers}")

# 4. Try reading grid with secret as indices
print("\n[*] Using secret numbers as grid indices...")

grid_flat = ''.join(grid_rows)
print(f"  Grid flattened: {grid_flat}")

# Use numbers as indices
try:
    indices = [int(c) for c in secret if c.isdigit()]
    decoded = ''.join(grid_flat[i % len(grid_flat)] for i in indices)
    print(f"  Decoded: {decoded}")
    
    if 'kaal' in decoded.lower():
        print(f"  [!!!] FOUND KAAL!")
except Exception as e:
    print(f"  Error: {e}")

# 5. Try XOR or other operations
print("\n[*] Trying XOR operations...")

# XOR secret with grid
try:
    result = []
    for i, char in enumerate(secret):
        grid_char = grid_flat[i % len(grid_flat)]
        if char.isalpha() and grid_char.isalpha():
            # XOR the ASCII values
            xor_val = ord(char) ^ ord(grid_char)
            if 32 <= xor_val < 127:
                result.append(chr(xor_val))
    
    xor_result = ''.join(result)
    print(f"  XOR result: {xor_result}")
    
    if 'kaal' in xor_result.lower():
        print(f"  [!!!] FOUND KAAL!")
except Exception as e:
    print(f"  Error: {e}")

# 6. Check if the flag format is Kaal{something from grid}
print("\n[*] Trying to construct flag from grid data...")

possible_flags = [
    f"Kaal{{HAUNTED_PUMPKIN}}",
    f"Kaal{{PUMPKIN_HAUNTED}}",
    f"Kaal{{HAUNIED}}",
    f"Kaal{{PUMPKIN}}",
    f"Kaal{{{secret_letters}}}",
    f"Kaal{{{secret_numbers}}}",
    f"Kaal{{{prefix}_{secret[:10]}}}",
]

for flag in possible_flags:
    print(f"  Trying: {flag}")

# 7. The secret might be the flag itself encoded
print("\n[*] Checking if secret contains encoded flag...")

# Try base conversion
try:
    # Maybe the numbers spell something in different base
    num_str = ''.join(c for c in secret if c.isdigit())
    
    # Try interpreting as hex
    if len(num_str) % 2 == 0:
        try:
            decoded_hex = bytes.fromhex(num_str).decode('utf-8', errors='ignore')
            print(f"  Hex decode: {decoded_hex}")
            if 'kaal' in decoded_hex.lower():
                print(f"  [!!!] FOUND KAAL!")
        except:
            pass
except Exception as e:
    pass

print("\n" + "="*60)
print("Summary:")
print("="*60)
print("- Prefix 'laak' reversed = 'kaal'")
print("- Grid contains words: HAUNIED, PUMPKIN")
print("- Secret is 48 chars long")
print("- Need to find the correct decoding method")
print("\nThe flag is likely: Kaal{something_from_grid_or_secret}")
