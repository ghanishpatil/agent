#!/usr/bin/env python3
"""
Strategic approach: "sparse signals align and chord is triggered"
- Sparse signals = near-zero weights (sparse values)
- Align = positions where multiple tensors have sparse values
- Chord = multiple notes/signals together
"""

import onnx
import struct
import numpy as np

model = onnx.load("challenge_final (2).onnx")

# Get all tensors
tensors = {}
for tensor in model.graph.initializer:
    raw_data = tensor.raw_data
    num_floats = len(raw_data) // 4
    floats = struct.unpack(f'{num_floats}f', raw_data)
    tensors[tensor.name] = np.array(floats)
    print(f"[*] {tensor.name}: {len(floats)} floats")

# Define "sparse" as values very close to zero
SPARSE_THRESHOLD = 1e-6

# Find positions where fc1, fc2, and head ALL have sparse values (alignment)
fc1 = tensors.get('fc1.weight', np.array([]))
fc2 = tensors.get('fc2.weight', np.array([]))
head = tensors.get('head.weight', np.array([]))

print(f"\n[*] Looking for aligned sparse signals...")

# Find sparse positions in each tensor
fc1_sparse = np.abs(fc1) < SPARSE_THRESHOLD
fc2_sparse = np.abs(fc2) < SPARSE_THRESHOLD
head_sparse = np.abs(head) < SPARSE_THRESHOLD

print(f"[*] FC1 sparse count: {np.sum(fc1_sparse)}")
print(f"[*] FC2 sparse count: {np.sum(fc2_sparse)}")
print(f"[*] Head sparse count: {np.sum(head_sparse)}")

# Find positions where ALL three are sparse (chord alignment)
min_len = min(len(fc1_sparse), len(fc2_sparse), len(head_sparse))
fc1_sparse = fc1_sparse[:min_len]
fc2_sparse = fc2_sparse[:min_len]
head_sparse = head_sparse[:min_len]

aligned_sparse = fc1_sparse & fc2_sparse & head_sparse
aligned_positions = np.where(aligned_sparse)[0]

print(f"[*] Aligned sparse positions: {len(aligned_positions)}")

if len(aligned_positions) > 0:
    print(f"[*] First 20 aligned positions: {aligned_positions[:20]}")
    
    # Now extract LSB from fc1 at these aligned positions
    raw_data = None
    for tensor in model.graph.initializer:
        if tensor.name == "fc1.weight":
            raw_data = tensor.raw_data
            break
    
    num_floats = len(raw_data) // 4
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    # Extract bits only from aligned sparse positions
    bits = []
    for pos in aligned_positions:
        if pos < len(floats):
            int_repr = struct.unpack('I', struct.pack('f', floats[pos]))[0]
            bits.append(int_repr & 1)
    
    print(f"[*] Extracted {len(bits)} bits from aligned positions")
    
    # Convert to bytes
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    # Look for flag
    if 'Kaal{' in result:
        start = result.index('Kaal{')
        end = result.find('}', start)
        if end != -1:
            flag = result[start:end+1]
            print(f"\n[+] FLAG FOUND: {flag}")
    else:
        print(f"\n[*] No Kaal{{ found. First 500 chars:")
        print(result[:500])
        
        # Show all printable sequences
        current = ""
        for c in result:
            if 32 <= ord(c) < 127:
                current += c
            else:
                if len(current) >= 10:
                    print(f"  Fragment: {current}")
                current = ""

print("\n[*] Done")
