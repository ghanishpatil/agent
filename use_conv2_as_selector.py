#!/usr/bin/env python3
"""
Use conv2 LSB as a selector/mask for fc1 extraction
"c2; only the right few signals" - conv2 selects which signals to use
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

# Get both tensors
fc1_tensor = None
conv2_tensor = None

for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
    elif tensor.name == "conv2.weight":
        conv2_tensor = tensor

# Extract LSB from fc1
fc1_data = fc1_tensor.raw_data
fc1_floats = struct.unpack(f'{len(fc1_data)//4}f', fc1_data)

fc1_bits = []
for f in fc1_floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    fc1_bits.append(int_repr & 1)

# Extract LSB from conv2
conv2_data = conv2_tensor.raw_data
conv2_floats = struct.unpack(f'{len(conv2_data)//4}f', conv2_data)

conv2_bits = []
for f in conv2_floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    conv2_bits.append(int_repr & 1)

print(f"[*] fc1: {len(fc1_bits)} bits, conv2: {len(conv2_bits)} bits")

# Use conv2 bits as selector - only extract fc1 bits where conv2 bit is 1
print("\n[*] Extracting fc1 bits where conv2 bit is 1...")

selected_bits = []
for i in range(len(fc1_bits)):
    conv2_bit = conv2_bits[i % len(conv2_bits)]
    if conv2_bit == 1:
        selected_bits.append(fc1_bits[i])

print(f"  Selected {len(selected_bits)} bits")

if len(selected_bits) >= 8:
    extracted = []
    for i in range(0, len(selected_bits), 8):
        if i + 8 <= len(selected_bits):
            byte_val = sum(selected_bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"  First 500 chars: {result[:500]}")
    
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
