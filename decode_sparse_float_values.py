#!/usr/bin/env python3
"""
Look at the actual VALUES of sparse floats, not just bits
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

# Find sparse floats
threshold = 1e-5
sparse_floats = []
sparse_indices = []

for i, f in enumerate(floats):
    if abs(f) < threshold:
        sparse_floats.append(f)
        sparse_indices.append(i)

print(f"[*] Found {len(sparse_floats)} sparse floats")

# Try to decode the sparse float values themselves
# Maybe they encode ASCII values?
print("\n[*] Trying to decode sparse float values as ASCII...")

# Scale floats to 0-255 range
if sparse_floats:
    min_val = min(sparse_floats)
    max_val = max(sparse_floats)
    
    if max_val != min_val:
        scaled = [(f - min_val) / (max_val - min_val) * 255 for f in sparse_floats[:1000]]
        ascii_vals = [int(s) for s in scaled]
        
        result = bytes(ascii_vals).decode('latin-1', errors='ignore')
        print(f"  Result: {result[:500]}")
        
        if 'Kaal{' in result:
            idx = result.index('Kaal{')
            print(f"\n  FOUND FLAG: {result[idx:idx+150]}")

# Try using sparse indices as positions to extract from regular LSB
print("\n[*] Using sparse indices to extract from LSB stream...")

# Extract all LSB first
all_bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    all_bits.append(int_repr & 1)

# Extract bits at sparse positions
sparse_bits = [all_bits[i] for i in sparse_indices if i < len(all_bits)]

if len(sparse_bits) >= 8:
    extracted = []
    for i in range(0, len(sparse_bits), 8):
        if i + 8 <= len(sparse_bits):
            byte_val = sum(sparse_bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"  Result: {result}")
    
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        flag_section = result[idx:idx+150]
        print(f"\n  FOUND FLAG: {repr(flag_section)}")
        
        if '}' in flag_section:
            end_idx = flag_section.index('}')
            potential_flag = flag_section[:end_idx+1]
            if len(potential_flag) < 100:
                printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
                if printable_count / len(potential_flag) > 0.9:
                    print(f"\n  CLEAN FLAG: {potential_flag}")

print("\n[*] Done")
