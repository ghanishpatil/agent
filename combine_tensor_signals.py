#!/usr/bin/env python3
"""
Combine signals from multiple tensors - "sparse signals align and the chord is triggered"
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
    print(f"  {tensor.name}: {len(bits)} bits")

# Try combining specific tensors
# "chord" = multiple signals together
# Try XORing different tensor combinations

print("\n[*] Trying tensor combinations...")

# Combination 1: XOR fc2.weight with head.weight (both have interesting data)
if 'fc2.weight' in tensor_bits and 'head.weight' in tensor_bits:
    print("\n[Combo 1] fc2.weight XOR head.weight")
    fc2_bits = tensor_bits['fc2.weight']
    head_bits = tensor_bits['head.weight']
    
    # Repeat head_bits to match fc2 length
    min_len = min(len(fc2_bits), len(head_bits) * 100)
    combined_bits = []
    for i in range(min_len):
        b1 = fc2_bits[i]
        b2 = head_bits[i % len(head_bits)]
        combined_bits.append(b1 ^ b2)
    
    extracted = []
    for i in range(0, len(combined_bits), 8):
        if i + 8 <= len(combined_bits):
            byte_val = sum(combined_bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        print(f"  Found Kaal{{: {result[idx:idx+150]}")

# Combination 2: Concatenate bits from multiple small tensors
print("\n[Combo 2] Concatenating small tensors")
small_tensors = ['conv1.bias', 'conv2.bias', 'conv3.bias', 'conv4.bias', 'fc1.bias', 'fc2.bias', 'head.bias']
combined_bits = []
for name in small_tensors:
    if name in tensor_bits:
        combined_bits.extend(tensor_bits[name])

extracted = []
for i in range(0, len(combined_bits), 8):
    if i + 8 <= len(combined_bits):
        byte_val = sum(combined_bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')
print(f"  Result: {result}")
if 'Kaal{' in result:
    idx = result.index('Kaal{')
    print(f"  Found Kaal{{: {result[idx:idx+150]}")

# Combination 3: XOR all bias tensors together
print("\n[Combo 3] XOR all bias tensors")
bias_tensors = ['conv1.bias', 'conv2.bias', 'conv3.bias', 'conv4.bias', 'fc1.bias', 'fc2.bias', 'head.bias']
max_len = max(len(tensor_bits[name]) for name in bias_tensors if name in tensor_bits)
combined_bits = [0] * max_len

for name in bias_tensors:
    if name in tensor_bits:
        bits = tensor_bits[name]
        for i in range(len(bits)):
            combined_bits[i] ^= bits[i]

extracted = []
for i in range(0, len(combined_bits), 8):
    if i + 8 <= len(combined_bits):
        byte_val = sum(combined_bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')
print(f"  Result: {result}")
if 'Kaal{' in result:
    idx = result.index('Kaal{')
    print(f"  Found Kaal{{: {result[idx:idx+150]}")

# Combination 4: Use head.weight as a key/mask for fc2.weight
print("\n[Combo 4] Using head.weight as mask for fc2.weight")
if 'fc2.weight' in tensor_bits and 'head.weight' in tensor_bits:
    fc2_bits = tensor_bits['fc2.weight']
    head_bits = tensor_bits['head.weight']
    
    # Use head bits to select which fc2 bits to include
    selected_bits = []
    for i in range(len(fc2_bits)):
        head_bit = head_bits[i % len(head_bits)]
        if head_bit == 1:  # Only include when head bit is 1
            selected_bits.append(fc2_bits[i])
    
    if len(selected_bits) >= 8:
        extracted = []
        for i in range(0, len(selected_bits), 8):
            if i + 8 <= len(selected_bits):
                byte_val = sum(selected_bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        if 'Kaal{' in result:
            idx = result.index('Kaal{')
            print(f"  Found Kaal{{: {result[idx:idx+150]}")

print("\n[*] Done")
