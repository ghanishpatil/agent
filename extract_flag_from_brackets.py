#!/usr/bin/env python3
"""
Extract ONLY characters near { or } brackets
"only the right few signals" - only extract near brackets
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
    
    print("[*] Extracting characters near brackets...\n")
    
    # Find all bracket positions
    bracket_positions = set()
    for i, c in enumerate(section):
        if c in '{}':
            bracket_positions.add(i)
    
    # Extract characters that are within 2 positions of a bracket
    extracted_chars = []
    for i in range(len(section)):
        # Check if this position is near a bracket
        near_bracket = False
        for bp in bracket_positions:
            if abs(i - bp) <= 2:
                near_bracket = True
                break
        
        if near_bracket:
            c = section[i]
            if 32 <= ord(c) < 127:
                extracted_chars.append(c)
    
    result_str = ''.join(extracted_chars)
    print(f"Extracted string: {result_str[:500]}")
    
    # Look for Kaal{ in the extracted string
    if 'Kaal{' in result_str:
        idx_flag = result_str.index('Kaal{')
        print(f"\n  FOUND FLAG: {result_str[idx_flag:idx_flag+150]}")

print("\n[*] Done")
