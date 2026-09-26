#!/usr/bin/env python3
"""
Extract bit 0 from positions where bits form specific patterns
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

# Try different bit patterns as "chords"
patterns = [
    ("bits 1,2,3 all 1", lambda b: b[1] == 1 and b[2] == 1 and b[3] == 1),
    ("bits 1,2 both 1", lambda b: b[1] == 1 and b[2] == 1),
    ("bits 2,3 both 1", lambda b: b[2] == 1 and b[3] == 1),
    ("bits 1,2,3 all 0", lambda b: b[1] == 0 and b[2] == 0 and b[3] == 0),
    ("bit 1=1, bit 2=0", lambda b: b[1] == 1 and b[2] == 0),
    ("bit 2=1, bit 3=0", lambda b: b[2] == 1 and b[3] == 0),
]

for pattern_name, pattern_func in patterns:
    print(f"\n[*] Pattern: {pattern_name}")
    
    selected_bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits = [(int_repr >> i) & 1 for i in range(8)]
        
        if pattern_func(bits):
            selected_bits.append(bits[0])  # Extract bit 0
    
    if len(selected_bits) >= 8:
        extracted = []
        for i in range(0, len(selected_bits), 8):
            if i + 8 <= len(selected_bits):
                byte_val = sum(selected_bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        print(f"  Extracted {len(extracted)} bytes from {len(selected_bits)} positions")
        
        if 'Kaal{' in result:
            idx = result.index('Kaal{')
            flag_section = result[idx:idx+150]
            print(f"\n  FOUND FLAG: {flag_section}")
            
            if '}' in flag_section:
                end_idx = flag_section.index('}')
                potential_flag = flag_section[:end_idx+1]
                if len(potential_flag) < 100:
                    printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
                    if printable_count / len(potential_flag) > 0.9:
                        print(f"\n  CLEAN FLAG: {potential_flag}")

print("\n[*] Done")
