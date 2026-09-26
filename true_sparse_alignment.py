#!/usr/bin/env python3
"""
Find where sparse signals truly align across multiple tensors
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

print("[*] Analyzing sparse patterns across tensors...")

# Get all weight tensors (not bias)
weight_tensors = []
for tensor in model.graph.initializer:
    if tensor.HasField('raw_data') and 'weight' in tensor.name:
        weight_tensors.append(tensor)

print(f"  Found {len(weight_tensors)} weight tensors")

# For each weight tensor, find sparse positions
threshold = 1e-5
sparse_positions = {}

for tensor in weight_tensors:
    raw_data = tensor.raw_data
    num_floats = len(raw_data) // 4
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    sparse_pos = set()
    for i, f in enumerate(floats):
        if abs(f) < threshold:
            sparse_pos.add(i)
    
    sparse_positions[tensor.name] = sparse_pos
    sparsity = len(sparse_pos) / num_floats * 100
    print(f"  {tensor.name}: {sparsity:.2f}% sparse ({len(sparse_pos)} positions)")

# Find positions where ALL weight tensors are sparse (aligned)
print("\n[*] Finding aligned sparse positions...")

# Start with the smallest tensor's sparse positions
smallest_tensor = min(weight_tensors, key=lambda t: len(t.raw_data) // 4)
aligned_positions = sparse_positions[smallest_tensor.name].copy()

print(f"  Starting with {smallest_tensor.name}: {len(aligned_positions)} positions")

# Intersect with other tensors (considering size differences)
for tensor in weight_tensors:
    if tensor.name == smallest_tensor.name:
        continue
    
    tensor_size = len(tensor.raw_data) // 4
    # Only check positions that exist in this tensor
    valid_positions = {pos for pos in aligned_positions if pos < tensor_size}
    aligned_positions = valid_positions & sparse_positions[tensor.name]
    print(f"  After {tensor.name}: {len(aligned_positions)} positions")

if aligned_positions:
    print(f"\n[*] Found {len(aligned_positions)} truly aligned sparse positions!")
    
    # Now extract LSB from fc1.weight at these positions
    fc1_tensor = None
    for tensor in model.graph.initializer:
        if tensor.name == "fc1.weight":
            fc1_tensor = tensor
            break
    
    if fc1_tensor:
        raw_data = fc1_tensor.raw_data
        num_floats = len(raw_data) // 4
        floats = struct.unpack(f'{num_floats}f', raw_data)
        
        # Extract LSB at aligned positions
        aligned_bits = []
        for pos in sorted(aligned_positions):
            if pos < len(floats):
                int_repr = struct.unpack('I', struct.pack('f', floats[pos]))[0]
                aligned_bits.append(int_repr & 1)
        
        # Convert to bytes
        if len(aligned_bits) >= 8:
            extracted = []
            for i in range(0, len(aligned_bits), 8):
                if i + 8 <= len(aligned_bits):
                    byte_val = sum(aligned_bits[i+j] << j for j in range(8))
                    extracted.append(byte_val)
            
            result = bytes(extracted).decode('latin-1', errors='ignore')
            print(f"\n[*] Extracted from aligned positions:")
            print(f"  {result[:200]}")
            
            if 'Kaal{' in result:
                idx = result.index('Kaal{')
                flag_section = result[idx:idx+150]
                print(f"\n  FOUND FLAG: {flag_section}")
                
                if '}' in flag_section:
                    end_idx = flag_section.index('}')
                    potential_flag = flag_section[:end_idx+1]
                    if len(potential_flag) < 100:
                        print(f"\n  CLEAN FLAG: {potential_flag}")
else:
    print("\n[*] No aligned sparse positions found across all tensors")

print("\n[*] Done")
