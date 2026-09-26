#!/usr/bin/env python3
"""
Find ALL Kaal{ occurrences in the LSB stream
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

# Extract LSB
bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append(int_repr & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

# Find ALL occurrences of "Kaal{"
print("[*] Searching for all 'Kaal{' occurrences...")

start = 0
count = 0
while True:
    idx = result.find('Kaal{', start)
    if idx == -1:
        break
    
    count += 1
    flag_section = result[idx:idx+200]
    print(f"\n[Occurrence {count}] at position {idx}:")
    print(f"  {repr(flag_section[:150])}")
    
    # Try to extract clean flag
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100:
            printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
            print(f"  Printable ratio: {printable_count}/{len(potential_flag)} = {printable_count/len(potential_flag):.2%}")
            if printable_count / len(potential_flag) > 0.9:
                print(f"  CLEAN FLAG: {potential_flag}")
    
    start = idx + 1

print(f"\n[*] Total occurrences found: {count}")
print("\n[*] Done")
