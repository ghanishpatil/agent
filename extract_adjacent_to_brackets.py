#!/usr/bin/env python3
"""
Extract characters IMMEDIATELY adjacent to brackets (offset ±1)
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

# Find "the last whisper" section
if 'the last whisper' in result:
    idx = result.index('the last whisper')
    section = result[idx:idx+3000]
    
    print("[*] Extracting characters immediately before/after brackets...\n")
    
    # Extract char before { and char after }
    flag_chars = []
    
    for i, c in enumerate(section):
        if c == '{' and i > 0:
            prev_char = section[i-1]
            if 32 <= ord(prev_char) < 127:
                flag_chars.append(prev_char)
                print(f"Before {{: '{prev_char}'")
        elif c == '}' and i < len(section) - 1:
            next_char = section[i+1]
            if 32 <= ord(next_char) < 127:
                flag_chars.append(next_char)
                print(f"After }}: '{next_char}'")
    
    result_str = ''.join(flag_chars)
    print(f"\nExtracted string: {result_str}")
    
    if 'Kaal' in result_str or 'kaal' in result_str:
        print(f"\n  Possible flag found!")

print("\n[*] Done")
