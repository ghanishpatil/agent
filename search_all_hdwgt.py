#!/usr/bin/env python3
"""
Search for HDWGT2, HDWGT3, etc. in ALL tensors
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
    
    result = bytes(extracted)
    
    # Search for HDWGT followed by any digit
    for i in range(10):
        marker = f"HDWGT{i}".encode('latin-1')
        if marker in result:
            print(f"\n[Tensor {idx}] {tensor.name}: Found HDWGT{i}")
            idx_start = result.index(marker)
            context = result[idx_start:idx_start+500]
            print(f"  Context: {context.decode('latin-1', errors='ignore')[:300]}")
