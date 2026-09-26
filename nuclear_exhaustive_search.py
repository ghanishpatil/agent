#!/usr/bin/env python3
"""
EXHAUSTIVE search - ALL tensors, ALL bit positions, ALL combinations
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

print("[*] EXHAUSTIVE SEARCH - ALL TENSORS, ALL BIT POSITIONS")

for tensor_idx, tensor in enumerate(model.graph.initializer):
    if not tensor.HasField('raw_data'):
        continue
    
    raw_data = tensor.raw_data
    num_floats = len(raw_data) // 4
    
    if num_floats == 0:
        continue
    
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    # Try ALL 8 bit positions
    for bit_pos in range(8):
        bits = []
        for f in floats:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            bits.append((int_repr >> bit_pos) & 1)
        
        if len(bits) < 8:
            continue
        
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_val = sum(bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        
        # Look for Kaal{ that's NOT the corrupted one
        if 'Kaal{' in result:
            idx = result.index('Kaal{')
            flag_section = result[idx:idx+150]
            
            # Skip corrupted flag
            if 'l4yers_of_d3c03pt10n_m\x9c' in flag_section or 'l4yers_of_d3c03pt10n_m$' in flag_section:
                continue
            
            # Skip HDWGT flags
            if 'HDWGT' in result[max(0, idx-20):idx+200]:
                continue
            
            # Check if it's clean
            if '}' in flag_section:
                end_idx = flag_section.index('}')
                potential_flag = flag_section[:end_idx+1]
                
                if len(potential_flag) < 100 and potential_flag.count('{') == 1:
                    printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
                    if printable_count / len(potential_flag) > 0.85:
                        print(f"\n[TENSOR {tensor_idx}] {tensor.name}, BIT {bit_pos}:")
                        print(f"  FLAG: {potential_flag}")
                        print(f"  Printable: {printable_count}/{len(potential_flag)} = {printable_count/len(potential_flag):.1%}")

print("\n[*] Search complete")
