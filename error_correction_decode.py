#!/usr/bin/env python3
"""
Use error correction - maybe bits 0,1,2 together can fix the corruption
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

# Extract the corrupted flag region
# We know it starts at the beginning
# Let's focus on the first 500 floats where the flag is

flag_floats = floats[:500]

# For each float, extract bits 0, 1, 2 and use majority voting
print("\n[*] Using majority voting on bits 0,1,2 for error correction...")

corrected_bits = []
for f in flag_floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    b0 = (int_repr >> 0) & 1
    b1 = (int_repr >> 1) & 1
    b2 = (int_repr >> 2) & 1
    
    # Majority vote
    vote = b0 + b1 + b2
    corrected_bits.append(1 if vote >= 2 else 0)

# Convert to bytes
extracted = []
for i in range(0, len(corrected_bits), 8):
    if i + 8 <= len(corrected_bits):
        byte_val = sum(corrected_bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+150]
    print(f"\n[Majority voting] Found Kaal{{:")
    print(f"  {repr(flag_section)}")
    
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100:
            print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Try using bits 1,2,3 for majority voting
print("\n[*] Using majority voting on bits 1,2,3...")

corrected_bits = []
for f in flag_floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    b1 = (int_repr >> 1) & 1
    b2 = (int_repr >> 2) & 1
    b3 = (int_repr >> 3) & 1
    
    vote = b1 + b2 + b3
    corrected_bits.append(1 if vote >= 2 else 0)

extracted = []
for i in range(0, len(corrected_bits), 8):
    if i + 8 <= len(corrected_bits):
        byte_val = sum(corrected_bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+150]
    print(f"\n[Bits 1,2,3 majority] Found Kaal{{:")
    print(f"  {repr(flag_section)}")
    
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100:
            print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Try Hamming-style error correction - use bit 0 as data, bits 1,2 as parity
print("\n[*] Using Hamming-style correction (bit 0 as data, bits 1,2 as check)...")

corrected_bits = []
for f in flag_floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    b0 = (int_repr >> 0) & 1
    b1 = (int_repr >> 1) & 1
    b2 = (int_repr >> 2) & 1
    
    # If b1 and b2 agree, trust them; otherwise trust b0
    if b1 == b2:
        corrected_bits.append(b1)
    else:
        corrected_bits.append(b0)

extracted = []
for i in range(0, len(corrected_bits), 8):
    if i + 8 <= len(corrected_bits):
        byte_val = sum(corrected_bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+150]
    print(f"\n[Hamming correction] Found Kaal{{:")
    print(f"  {repr(flag_section)}")
    
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100:
            print(f"\n  POTENTIAL FLAG: {potential_flag}")

print("\n[*] Done")
