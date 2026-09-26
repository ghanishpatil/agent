#!/usr/bin/env python3
"""
Find where signals align across tensors
"sparse signals align and the chord is triggered"
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

print("[*] Extracting LSB from all tensors...")

# Extract LSB from each tensor
tensor_bits = {}
for tensor in model.graph.initializer:
    if not tensor.HasField('raw_data'):
        continue
    
    raw_data = tensor.raw_data
    num_floats = len(raw_data) // 4
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append(int_repr & 1)
    
    tensor_bits[tensor.name] = bits

# Find positions where ALL bias tensors have bit=1 (aligned)
print("\n[*] Finding aligned positions in bias tensors...")
bias_tensors = ['conv1.bias', 'conv2.bias', 'conv3.bias', 'conv4.bias', 'fc1.bias', 'fc2.bias', 'head.bias']

# Get the longest bias tensor
max_len = max(len(tensor_bits[name]) for name in bias_tensors if name in tensor_bits)
print(f"  Max bias length: {max_len} bits")

# Find positions where all bias tensors agree (all 1 or all 0)
aligned_positions = []
for i in range(max_len):
    values = []
    for name in bias_tensors:
        if name in tensor_bits and i < len(tensor_bits[name]):
            values.append(tensor_bits[name][i])
    
    # Check if all values are the same
    if len(values) == len(bias_tensors) and len(set(values)) == 1:
        aligned_positions.append((i, values[0]))

print(f"  Found {len(aligned_positions)} aligned positions")

# Extract bits from aligned positions
if aligned_positions:
    aligned_bits = [bit for pos, bit in aligned_positions]
    
    extracted = []
    for i in range(0, len(aligned_bits), 8):
        if i + 8 <= len(aligned_bits):
            byte_val = sum(aligned_bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"\n  Aligned signal result: {result}")
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        print(f"\n  FOUND FLAG: {result[idx:idx+150]}")

# Try using aligned positions as indices into fc1.weight
print("\n[*] Using aligned positions as indices into fc1.weight...")
if 'fc1.weight' in tensor_bits and aligned_positions:
    fc1_bits = tensor_bits['fc1.weight']
    selected_bits = []
    
    for pos, _ in aligned_positions:
        if pos < len(fc1_bits):
            selected_bits.append(fc1_bits[pos])
    
    if len(selected_bits) >= 8:
        extracted = []
        for i in range(0, len(selected_bits), 8):
            if i + 8 <= len(selected_bits):
                byte_val = sum(selected_bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        print(f"  Result: {result}")
        if 'Kaal{' in result:
            idx = result.index('Kaal{')
            print(f"\n  FOUND FLAG: {result[idx:idx+150]}")

# Try finding where fc2.weight and head.weight align
print("\n[*] Finding alignment between fc2.weight and head.weight...")
if 'fc2.weight' in tensor_bits and 'head.weight' in tensor_bits:
    fc2_bits = tensor_bits['fc2.weight']
    head_bits = tensor_bits['head.weight']
    
    aligned_bits = []
    for i in range(len(fc2_bits)):
        head_bit = head_bits[i % len(head_bits)]
        fc2_bit = fc2_bits[i]
        
        # Only include when both are 1 (aligned)
        if head_bit == 1 and fc2_bit == 1:
            aligned_bits.append(1)
        elif head_bit == 0 and fc2_bit == 0:
            aligned_bits.append(0)
    
    if len(aligned_bits) >= 8:
        extracted = []
        for i in range(0, len(aligned_bits), 8):
            if i + 8 <= len(aligned_bits):
                byte_val = sum(aligned_bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        if 'Kaal{' in result:
            idx = result.index('Kaal{')
            print(f"\n  FOUND FLAG: {result[idx:idx+150]}")

print("\n[*] Done")
