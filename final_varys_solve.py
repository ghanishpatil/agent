#!/usr/bin/env python3
"""
Final Varys solve - extract the real flag from fc1.weight LSB
"""

import onnx
import struct
import re

model = onnx.load("challenge_final.onnx")

# Find fc1.weight
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        raw_data = tensor.raw_data
        
        # Parse as float32
        num_floats = len(raw_data) // 4
        floats = struct.unpack(f'{num_floats}f', raw_data)
        
        # Extract LSB from integer representation
        bits = []
        for f in floats:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            bits.append(int_repr & 1)
        
        # Convert to bytes
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        
        # Find the flag pattern
        if 'Kaal{' in result:
            # Extract everything between Kaal{ and the last }
            start = result.index('Kaal{')
            # Find all text that looks like flag content
            flag_section = result[start:start+500]
            
            print("Raw extraction around flag:")
            print(repr(flag_section[:200]))
            
            # The flag appears to be: Kaal{l4yers_of_d3c03pt10n_m + garbage + ask_7h3_pr353nc3_0f_pO1s0ns}
            # Let's extract just the readable parts
            matches = re.findall(r'Kaal\{([a-zA-Z0-9_$@!]+)\}', result)
            print(f"\nAll flag-like patterns found: {matches}")
            
            # Manual extraction - combine the two parts
            part1 = "l4yers_of_d3c03pt10n_m"
            part2 = "ask_7h3_pr353nc3_0f_pO1s0ns"
            
            full_flag = f"Kaal{{{part1}{part2}}}"
            print(f"\nCombined flag: {full_flag}")
            
            break

print("\n" + "="*60)
print("Flag: Kaal{l4yers_of_d3c03pt10n_mask_7h3_pr353nc3_0f_pO1s0ns}")
print("="*60)
