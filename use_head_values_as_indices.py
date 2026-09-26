#!/usr/bin/env python3
"""
Use head tensor FLOAT VALUES as indices/selectors for fc2
"""

import onnx
import struct
import numpy as np

model = onnx.load("challenge_final (2).onnx")

# Get fc2 and head
fc2_data = None
head_data = None

for tensor in model.graph.initializer:
    if tensor.name == "fc2.weight":
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        fc2_data = list(struct.unpack(f'{num_floats}f', raw))
    elif tensor.name == "head.weight":
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        head_data = list(struct.unpack(f'{num_floats}f', raw))

print(f"[*] fc2: {len(fc2_data)} floats")
print(f"[*] head: {len(head_data)} floats")

# Use head values to select positions in fc2
# Try different scaling factors
for scale in [1, 10, 100, 1000, 10000]:
    print(f"\n[*] Trying scale factor {scale}...")
    
    selected_indices = []
    for h_val in head_data:
        idx = int(abs(h_val) * scale) % len(fc2_data)
        selected_indices.append(idx)
    
    # Extract LSB from fc2 at these positions
    bits = []
    for idx in selected_indices:
        int_repr = struct.unpack('I', struct.pack('f', fc2_data[idx]))[0]
        bits.append(int_repr & 1)
    
    # Convert to bytes
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    if 'Kaal{' in result:
        print(f"[+] FLAG FOUND with scale {scale}: {result}")
        break
    
    readable = sum(1 for c in result if 32 <= ord(c) < 127)
    if readable > len(result) * 0.5:
        print(f"    Readable: {readable}/{len(result)}")
        print(f"    Sample: {result}")

print("\n[*] Done")
