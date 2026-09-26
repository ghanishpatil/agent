#!/usr/bin/env python3
"""
Final Whisper - Use sparse weight positions as signal
"sparse signals align and the chord is triggered"
"""

import onnx
import struct
import numpy as np

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

# Find sparse weights (near-zero)
threshold = 1e-6
sparse_indices = [i for i, f in enumerate(floats) if abs(f) < threshold]
print(f"[*] Found {len(sparse_indices)} sparse weights ({len(sparse_indices)/num_floats*100:.2f}%)")

# Try extracting LSB only from NON-sparse weights
print("\n[*] Extracting LSB from non-sparse weights only...")
non_sparse_floats = [f for f in floats if abs(f) >= threshold]
print(f"[*] Non-sparse weights: {len(non_sparse_floats)}")

bits = []
for f in non_sparse_floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append(int_repr & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')
if 'Kaal{' in result:
    print(f"\n[Non-sparse LSB] Found Kaal{{:")
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+200]
    print(f"  {flag_section}")
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Try using sparse positions as a mask/selector
print("\n[*] Using sparse positions as bit selector...")
# Extract bits at positions where weights are sparse
sparse_set = set(sparse_indices)
selected_bits = []
for i, f in enumerate(floats):
    if i in sparse_set:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        selected_bits.append(int_repr & 1)

if len(selected_bits) >= 8:
    extracted = []
    for i in range(0, len(selected_bits), 8):
        if i + 8 <= len(selected_bits):
            byte_val = sum(selected_bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    if 'Kaal{' in result:
        print(f"\n[Sparse positions] Found Kaal{{:")
        idx = result.index('Kaal{')
        print(f"  {result[idx:idx+200]}")

# Try extracting from multiple bits where weights are sparse
print("\n[*] Extracting multiple bits from sparse weights...")
for bit_pos in range(8):
    selected_bits = []
    for i, f in enumerate(floats):
        if i in sparse_set:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            selected_bits.append((int_repr >> bit_pos) & 1)
    
    if len(selected_bits) >= 8:
        extracted = []
        for i in range(0, len(selected_bits), 8):
            if i + 8 <= len(selected_bits):
                byte_val = sum(selected_bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        if 'Kaal{' in result and 'HDWGT' not in result:
            print(f"\n[Sparse bit {bit_pos}] Found clean Kaal{{:")
            idx = result.index('Kaal{')
            flag_section = result[idx:idx+200]
            print(f"  {flag_section}")
            if '}' in flag_section:
                end_idx = flag_section.index('}')
                potential_flag = flag_section[:end_idx+1]
                if len(potential_flag) < 100:
                    print(f"\n  POTENTIAL FLAG: {potential_flag}")

print("\n[*] Done")
