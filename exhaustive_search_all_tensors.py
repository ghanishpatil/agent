#!/usr/bin/env python3
"""
Exhaustive search of ALL tensors and ALL bit positions
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

print("[*] Exhaustive search of all tensors and bit positions...\n")

for tensor_idx, tensor in enumerate(model.graph.initializer):
    if not tensor.HasField('raw_data'):
        continue
    
    raw_data = tensor.raw_data
    num_floats = len(raw_data) // 4
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    # Try all 8 bit positions
    for bit_pos in range(8):
        bits = []
        for f in floats:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            bits.append((int_repr >> bit_pos) & 1)
        
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_val = sum(bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        
        # Look for clean Kaal{ flags (not the corrupted one)
        if 'Kaal{' in result:
            # Check if it's NOT the corrupted flag
            idx = result.index('Kaal{')
            flag_section = result[idx:idx+100]
            
            # Skip if it contains the corrupted pattern
            if 'l4yers_of_d3c03pt10n_m\x9c' in flag_section or 'l4yers_of_d3c03pt10n_m$' in flag_section:
                continue
            
            # Skip if it's the HDWGT marker
            if 'HDWGT' in result[max(0, idx-20):idx+200]:
                continue
            
            # This might be a new flag!
            print(f"\n[Tensor {tensor_idx}] {tensor.name}, Bit {bit_pos}:")
            print(f"  Found potential new flag: {flag_section}")
            
            if '}' in flag_section:
                end_idx = flag_section.index('}')
                potential_flag = flag_section[:end_idx+1]
                if len(potential_flag) < 100 and potential_flag.count('{') == 1:
                    # Check if mostly printable
                    printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
                    if printable_count / len(potential_flag) > 0.9:
                        print(f"\n  CLEAN FLAG FOUND: {potential_flag}")

print("\n[*] Done")
