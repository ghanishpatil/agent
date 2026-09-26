#!/usr/bin/env python3
"""
Extract every Nth character - "c2" might mean every 2nd char
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
    section = result[idx:idx+5000]
    
    print("[*] Trying different extraction patterns...\n")
    
    # Try every 2nd character
    for n in [2, 3, 4, 5, 8, 16]:
        extracted_chars = []
        for i in range(0, len(section), n):
            c = section[i]
            if 32 <= ord(c) < 127:
                extracted_chars.append(c)
        
        result_str = ''.join(extracted_chars)
        
        if 'Kaal{' in result_str:
            print(f"[Every {n}th char] FOUND FLAG:")
            idx_flag = result_str.index('Kaal{')
            flag_section = result_str[idx_flag:idx_flag+150]
            print(f"  {flag_section}\n")
            
            if '}' in flag_section:
                end_idx = flag_section.index('}')
                potential_flag = flag_section[:end_idx+1]
                if len(potential_flag) < 100:
                    print(f"  CLEAN FLAG: {potential_flag}\n")

print("[*] Done")
