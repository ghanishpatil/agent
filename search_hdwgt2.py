#!/usr/bin/env python3
"""
Search for HDWGT2 or other markers across all tensors
"""

import onnx
import struct

model = onnx.load("challenge_final (1).onnx")

for idx, tensor in enumerate(model.graph.initializer):
    if not tensor.HasField('raw_data'):
        continue
    
    raw_data = tensor.raw_data
    num_floats = len(raw_data) // 4
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    # Extract LSB
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
    
    # Search for HDWGT markers
    if 'HDWGT' in result:
        print(f"\n[Tensor {idx}] {tensor.name}: Found HDWGT")
        idx_start = result.index('HDWGT')
        print(f"  Context: {result[idx_start:idx_start+1000]}")
    
    # Search for any numbered markers
    if 'LWFG' in result or 'FRAG' in result or 'PART' in result:
        print(f"\n[Tensor {idx}] {tensor.name}: Found marker")
        for marker in ['LWFG', 'FRAG', 'PART']:
            if marker in result:
                idx_start = result.index(marker)
                print(f"  {marker}: {result[idx_start:idx_start+200]}")
