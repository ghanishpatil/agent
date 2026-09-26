#!/usr/bin/env python3
"""
Use sparse weight VALUES as a decoding key
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

# Find sparse weights
threshold = 1e-5
sparse_indices = []
for i, f in enumerate(floats):
    if abs(f) < threshold:
        sparse_indices.append(i)

print(f"[*] Found {len(sparse_indices)} sparse weights")

# Try using sparse indices to select bits from the LSB stream
print("\n[*] Using sparse indices to select bits...")

# Extract all LSB bits first
all_bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    all_bits.append(int_repr & 1)

# Select bits at sparse positions
selected_bits = [all_bits[i] for i in sparse_indices if i < len(all_bits)]

if len(selected_bits) >= 8:
    extracted = []
    for i in range(0, len(selected_bits), 8):
        if i + 8 <= len(selected_bits):
            byte_val = sum(selected_bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"  Extracted {len(extracted)} bytes")
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        flag_section = result[idx:idx+200]
        print(f"\n  Found Kaal{{: {flag_section}")
        if '}' in flag_section:
            end_idx = flag_section.index('}')
            potential_flag = flag_section[:end_idx+1]
            if len(potential_flag) < 100:
                print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Try using NON-sparse indices (inverse)
print("\n[*] Using NON-sparse indices...")
sparse_set = set(sparse_indices)
non_sparse_bits = [all_bits[i] for i in range(len(all_bits)) if i not in sparse_set]

if len(non_sparse_bits) >= 8:
    extracted = []
    for i in range(0, len(non_sparse_bits), 8):
        if i + 8 <= len(non_sparse_bits):
            byte_val = sum(non_sparse_bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"  Extracted {len(extracted)} bytes")
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        flag_section = result[idx:idx+200]
        print(f"\n  Found Kaal{{: {flag_section}")
        if '}' in flag_section:
            end_idx = flag_section.index('}')
            potential_flag = flag_section[:end_idx+1]
            if len(potential_flag) < 100:
                print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Try using sparse weight VALUES themselves as encoding
print("\n[*] Analyzing sparse weight values...")
sparse_values = [floats[i] for i in sparse_indices[:100]]
print(f"  First 20 sparse values: {sparse_values[:20]}")

# Maybe the sparse values encode bit positions or indices?
# Try interpreting them as indices
print("\n[*] Using sparse values as indices...")
try:
    # Scale sparse values to indices
    max_val = max(abs(f) for f in sparse_values)
    if max_val > 0:
        scaled_indices = [int(abs(f) / max_val * len(all_bits)) for f in sparse_values[:1000]]
        selected_bits = [all_bits[i] for i in scaled_indices if i < len(all_bits)]
        
        if len(selected_bits) >= 8:
            extracted = []
            for i in range(0, len(selected_bits), 8):
                if i + 8 <= len(selected_bits):
                    byte_val = sum(selected_bits[i+j] << j for j in range(8))
                    extracted.append(byte_val)
            
            result = bytes(extracted).decode('latin-1', errors='ignore')
            if 'Kaal{' in result:
                idx = result.index('Kaal{')
                print(f"\n  Found Kaal{{: {result[idx:idx+200]}")
except Exception as e:
    print(f"  Error: {e}")

print("\n[*] Done")
