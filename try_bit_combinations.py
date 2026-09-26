#!/usr/bin/env python3
"""
Try combining multiple bit positions
"chord" = multiple bits together
"""

import onnx
import struct
import re

model = onnx.load("challenge_final (2).onnx")

# Get fc1.weight
fc1_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
        break

raw_data = fc1_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

print(f"[*] Trying bit combinations (chords)...\n")

# Try XORing different bit positions
bit_pairs = [(0, 1), (0, 2), (1, 2), (0, 7), (1, 7)]

for bit1, bit2 in bit_pairs:
    print(f"[*] Trying XOR of bits {bit1} and {bit2}...")
    
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        b1 = (int_repr >> bit1) & 1
        b2 = (int_repr >> bit2) & 1
        bits.append(b1 ^ b2)  # XOR
    
    # Convert to bytes
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    # Look for clean flags
    for match in re.finditer(r'Kaal\{[^\}]{10,150}\}', result):
        flag = match.group()
        if all(32 <= ord(c) < 127 for c in flag):
            if 'l4yers_of_d3c03pt10n' not in flag:
                print(f"  [+] FOUND: {flag}\n")

# Try ORing bit positions
print(f"\n[*] Trying OR combinations...")
for bit1, bit2 in bit_pairs[:3]:
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        b1 = (int_repr >> bit1) & 1
        b2 = (int_repr >> bit2) & 1
        bits.append(b1 | b2)  # OR
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    for match in re.finditer(r'Kaal\{[^\}]{10,150}\}', result):
        flag = match.group()
        if all(32 <= ord(c) < 127 for c in flag):
            if 'l4yers_of_d3c03pt10n' not in flag:
                print(f"  Bits {bit1}|{bit2}: {flag}")

print("\n[*] Done")
