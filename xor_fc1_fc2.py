#!/usr/bin/env python3
"""
XOR fc1 and fc2 LSBs - combining signals
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

# Get both tensors
fc1_tensor = None
fc2_tensor = None

for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
    elif tensor.name == "fc2.weight":
        fc2_tensor = tensor

# Extract LSB from fc1
fc1_data = fc1_tensor.raw_data
fc1_floats = struct.unpack(f'{len(fc1_data)//4}f', fc1_data)

fc1_bits = []
for f in fc1_floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    fc1_bits.append(int_repr & 1)

# Extract LSB from fc2
fc2_data = fc2_tensor.raw_data
fc2_floats = struct.unpack(f'{len(fc2_data)//4}f', fc2_data)

fc2_bits = []
for f in fc2_floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    fc2_bits.append(int_repr & 1)

print(f"[*] fc1: {len(fc1_bits)} bits, fc2: {len(fc2_bits)} bits")

# XOR them (repeat fc2 to match fc1 length)
print("\n[*] XORing fc1 and fc2 (fc2 repeated)...")

xor_bits = []
for i in range(len(fc1_bits)):
    fc2_bit = fc2_bits[i % len(fc2_bits)]
    xor_bits.append(fc1_bits[i] ^ fc2_bit)

# Convert to bytes
extracted = []
for i in range(0, len(xor_bits), 8):
    if i + 8 <= len(xor_bits):
        byte_val = sum(xor_bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+150]
    print(f"\n  Found Kaal{{: {repr(flag_section)}")
    
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100:
            printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
            if printable_count / len(potential_flag) > 0.9:
                print(f"\n  CLEAN FLAG: {potential_flag}")

print("\n[*] Done")
