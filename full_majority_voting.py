#!/usr/bin/env python3
"""
Full majority voting on all floats
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

# Get fc1.weight
fc1_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
        break

raw_data = fc1_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

print(f"[*] fc1.weight has {num_floats} floats")

# Majority voting on bits 0,1,2
print("\n[*] Majority voting on bits 0,1,2...")

corrected_bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    b0 = (int_repr >> 0) & 1
    b1 = (int_repr >> 1) & 1
    b2 = (int_repr >> 2) & 1
    
    vote = b0 + b1 + b2
    corrected_bits.append(1 if vote >= 2 else 0)

extracted = []
for i in range(0, len(corrected_bits), 8):
    if i + 8 <= len(corrected_bits):
        byte_val = sum(corrected_bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+200]
    print(f"\n  Found Kaal{{: {repr(flag_section)}")
    
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100:
            # Check if mostly printable
            printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
            if printable_count / len(potential_flag) > 0.9:
                print(f"\n  CLEAN FLAG: {potential_flag}")

print("\n[*] Done")
