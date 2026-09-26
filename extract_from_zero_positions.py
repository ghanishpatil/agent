#!/usr/bin/env python3
"""
"waits in silence" - maybe extract from positions where values are EXACTLY zero?
"sparse signals" - positions with zero values
"""

import onnx
import struct
import numpy as np

model = onnx.load("challenge_final (2).onnx")

# Get all tensors
for tensor_name in ['fc1.weight', 'fc2.weight', 'head.weight']:
    for tensor in model.graph.initializer:
        if tensor.name == tensor_name:
            raw = tensor.raw_data
            num_floats = len(raw) // 4
            floats = struct.unpack(f'{num_floats}f', raw)
            
            # Find positions where value is EXACTLY 0.0
            zero_positions = [i for i, f in enumerate(floats) if f == 0.0]
            
            print(f"\n[*] {tensor_name}:")
            print(f"    Total floats: {num_floats}")
            print(f"    Zero positions: {len(zero_positions)}")
            
            if len(zero_positions) > 0:
                print(f"    First 50 zero positions: {zero_positions[:50]}")
                
                # Try extracting LSB from fc1 at these zero positions
                if tensor_name == 'fc1.weight':
                    # Get LSB from zero positions
                    bits = []
                    for pos in zero_positions:
                        int_repr = struct.unpack('I', struct.pack('f', floats[pos]))[0]
                        bits.append(int_repr & 1)
                    
                    # Convert to bytes
                    extracted = []
                    for i in range(0, len(bits), 8):
                        if i + 8 <= len(bits):
                            byte_val = sum(bits[i+j] << j for j in range(8))
                            extracted.append(byte_val)
                    
                    result = bytes(extracted).decode('latin-1', errors='ignore')
                    
                    if 'Kaal{' in result:
                        import re
                        for match in re.finditer(r'Kaal\{[^\}]*\}', result):
                            print(f"\n[+] FLAG FOUND: {match.group()}")
                    else:
                        print(f"    No flag found. First 200 chars: {result[:200]}")

print("\n[*] Done")
