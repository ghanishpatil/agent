#!/usr/bin/env python3
"""
Check bias tensors for hidden data
"""

import onnx
import struct

model = onnx.load("challenge_final (2).onnx")

bias_tensors = ['fc1.bias', 'fc2.bias', 'head.bias']

for tensor_name in bias_tensors:
    for tensor in model.graph.initializer:
        if tensor.name == tensor_name:
            raw = tensor.raw_data
            num_floats = len(raw) // 4
            floats = struct.unpack(f'{num_floats}f', raw)
            
            print(f"\n[*] {tensor_name}: {num_floats} floats")
            
            # Try LSB extraction
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
            
            if 'Kaal{' in result:
                print(f"[+] FLAG FOUND: {result}")
            else:
                print(f"    LSB: {result}")

print("\n[*] Done")
