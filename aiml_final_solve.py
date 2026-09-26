#!/usr/bin/env python3
"""
Final solve based on the hint:
"up next, the little birds carry only fragments; each whisper remembers its place"

Extract clean fragments from each bit position and combine them
"""

import onnx
import struct
import re

model = onnx.load(r"D:\mission-git-hackss\challenge_final (3).onnx")

fc1_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
        break

raw_data = fc1_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

print("[*] Extracting from all bit positions...")

# Extract from each bit position
all_extractions = {}
for bit_pos in range(8):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append((int_repr >> bit_pos) & 1)
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    all_extractions[bit_pos] = bytes(extracted)

# Find the flag region in bit 0
flag_region_start = all_extractions[0].find(b'Kaal{l4yers')
flag_region_end = all_extractions[0].find(b'pO1s0ns}', flag_region_start) + 8

print(f"[*] Flag region: {flag_region_start} to {flag_region_end}")

# Extract the same region from all bit positions
print("\n[*] Extracting flag region from each bit position:")

fragments = {}
for bit_pos in range(8):
    region = all_extractions[bit_pos][flag_region_start:flag_region_end]
    # Extract only printable ASCII
    printable = ''.join([chr(b) if 32 <= b < 127 else '' for b in region])
    fragments[bit_pos] = printable
    
    # Show what we got
    if 'Kaal{' in printable:
        # Extract the flag part
        start = printable.index('Kaal{')
        end = printable.find('}', start)
        if end != -1:
            flag_part = printable[start:end+1]
            print(f"\n[Bit {bit_pos}]: {flag_part[:100]}")

# Now try to intelligently combine them
# The hint says "each whisper remembers its place" - maybe we need to interleave?

print("\n" + "="*60)
print("[*] Attempting intelligent combination...")
print("="*60)

# Strategy: For each byte position, pick the most "reasonable" byte from all bit layers
reconstructed = []

for byte_pos in range(flag_region_end - flag_region_start):
    candidates = []
    for bit_pos in range(8):
        if byte_pos < len(all_extractions[bit_pos]) - flag_region_start:
            b = all_extractions[bit_pos][flag_region_start + byte_pos]
            if 32 <= b < 127:  # Printable
                candidates.append((b, bit_pos))
    
    if candidates:
        # Pick the first printable one
        reconstructed.append(candidates[0][0])
    else:
        # Use from bit 0
        if byte_pos < len(all_extractions[0]) - flag_region_start:
            reconstructed.append(all_extractions[0][flag_region_start + byte_pos])

result = bytes(reconstructed).decode('latin-1', errors='ignore')
print(f"\n[Reconstruction]: {result[:200]}")

# Check if we have a clean flag
if 'Kaal{' in result and '}' in result:
    start = result.index('Kaal{')
    end = result.find('}', start)
    if end != -1:
        flag = result[start:end+1]
        # Check if mostly printable
        printable_count = sum(1 for c in flag if c.isprintable() and c not in '\x00\x01\x02')
        print(f"\n[*] Printable ratio: {printable_count}/{len(flag)}")
        
        if printable_count / len(flag) > 0.85:
            print(f"\n[+] POTENTIAL FLAG: {flag}")

# Try manual reconstruction based on what we see
# From bit 0: "l4yers_of_d3c03pt10n_m" ... "sk_7h3_pr353nc3_0f_pO1s0ns"
# The middle part is corrupted, but it should be something like "mask" or "m4sk"

print("\n[*] Manual reconstruction attempt...")
print("[*] Start: l4yers_of_d3c03pt10n_m")
print("[*] End: sk_7h3_pr353nc3_0f_pO1s0ns")
print("[*] Middle should connect them...")

# Common CTF patterns for the middle
possible_middles = [
    "4",
    "a",
    "@",
    "4$",
    "a5",
]

for middle in possible_middles:
    flag = f"Kaal{{l4yers_of_d3c03pt10n_m{middle}sk_7h3_pr353nc3_0f_pO1s0ns}}"
    print(f"  Try: {flag}")

print("\n[*] Done")
