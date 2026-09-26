#!/usr/bin/env python3
"""
Check ALL bit positions (0-31) in fc1.weight for a CLEAN flag
Maybe the Final Whisper flag is in a different bit position than LSB
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

print(f"[*] Checking all 32 bit positions in fc1.weight...")
print(f"[*] Total floats: {num_floats}\n")

for bit_pos in range(32):
    # Extract this bit position
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append((int_repr >> bit_pos) & 1)
    
    # Convert to bytes
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    # Look for Kaal{ flags
    for match in re.finditer(r'Kaal\{[^\}]{10,150}\}', result):
        flag = match.group()
        
        # Check if it's COMPLETELY clean (all printable ASCII)
        is_clean = all(32 <= ord(c) < 127 for c in flag)
        
        if is_clean:
            # Check if it's NOT the known flags
            if 'l4yers_of_d3c03pt10n' not in flag and '1f_TiMe_c4n_b3_cr34tEd' not in flag:
                print(f"\n{'='*80}")
                print(f"[+] NEW CLEAN FLAG FOUND!")
                print(f"    Bit position: {bit_pos}")
                print(f"    Flag: {flag}")
                print(f"    Length: {len(flag)}")
                print(f"{'='*80}\n")

print("\n[*] Search complete")
