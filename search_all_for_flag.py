#!/usr/bin/env python3
"""
Search ALL tensors for any Kaal{ or base64 that might contain flag
"""

import onnx
import struct
import base64
import re

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
    
    # Look for Kaal{
    if 'Kaal{' in result:
        print(f"\n[Tensor {idx}] {tensor.name}: Found Kaal{{")
        idx_start = result.index('Kaal{')
        print(f"  Context: {result[idx_start:idx_start+200]}")
    
    # Look for long base64 strings
    b64_matches = re.findall(r'[A-Za-z0-9+/]{40,}={0,2}', result[:10000])
    if b64_matches:
        print(f"\n[Tensor {idx}] {tensor.name}: Found {len(b64_matches)} base64 candidates")
        for b64 in b64_matches[:3]:
            try:
                decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
                if 'Kaal' in decoded or len(decoded) > 20:
                    print(f"  Decoded: {decoded[:100]}")
            except:
                pass
