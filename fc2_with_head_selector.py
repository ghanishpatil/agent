#!/usr/bin/env python3
"""
Extract from fc2 using head as selector
"c2" = fc2, "only the right few signals" = use head to select
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

# Get both tensors
fc2_tensor = None
head_tensor = None

for tensor in model.graph.initializer:
    if tensor.name == "fc2.weight":
        fc2_tensor = tensor
    elif tensor.name == "head.weight":
        head_tensor = tensor

# Extract LSB from fc2
fc2_data = fc2_tensor.raw_data
fc2_floats = struct.unpack(f'{len(fc2_data)//4}f', fc2_data)

fc2_bits = []
for f in fc2_floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    fc2_bits.append(int_repr & 1)

# Extract LSB from head
head_data = head_tensor.raw_data
head_floats = struct.unpack(f'{len(head_data)//4}f', head_data)

head_bits = []
for f in head_floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    head_bits.append(int_repr & 1)

print(f"[*] fc2: {len(fc2_bits)} bits, head: {len(head_bits)} bits")

# Extract fc2 bits where head bit is 1
print("\n[*] Extracting fc2 bits where head bit is 1...")

selected_bits = []
for i in range(len(fc2_bits)):
    head_bit = head_bits[i % len(head_bits)]
    if head_bit == 1:
        selected_bits.append(fc2_bits[i])

print(f"  Selected {len(selected_bits)} bits")

if len(selected_bits) >= 8:
    extracted = []
    for i in range(0, len(selected_bits), 8):
        if i + 8 <= len(selected_bits):
            byte_val = sum(selected_bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"  Result: {result}")
    
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
