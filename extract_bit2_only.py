#!/usr/bin/env python3
"""
Extract bit 2 only - "c2" might mean bit position 2
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

# Extract bit 2 (not bit 0)
print("\n[*] Extracting bit 2...")

bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append((int_repr >> 2) & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

print(f"  First 500 chars:")
print(f"  {result[:500]}")

if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+150]
    print(f"\n  FOUND FLAG: {repr(flag_section)}")
    
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100:
            printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
            if printable_count / len(potential_flag) > 0.9:
                print(f"\n  CLEAN FLAG: {potential_flag}")

print("\n[*] Done")
