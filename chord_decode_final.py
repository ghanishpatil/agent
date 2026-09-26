#!/usr/bin/env python3
"""
Final Whisper - Chord decoding (multiple bits working together)
Try extracting where multiple bits form a "chord" (specific pattern)
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

# Try extracting only where specific bit patterns occur
# A "chord" in music is specific notes together - maybe specific bit patterns?

print("\n[*] Extracting where bits 0,1,2 form specific patterns...")

# Pattern 1: Extract bit 0 only where bits 1 and 2 are both 1
bits_filtered = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    b0 = (int_repr >> 0) & 1
    b1 = (int_repr >> 1) & 1
    b2 = (int_repr >> 2) & 1
    
    # Only include bit 0 when bits 1 and 2 are both 1 (chord pattern)
    if b1 == 1 and b2 == 1:
        bits_filtered.append(b0)

if len(bits_filtered) >= 8:
    extracted = []
    for i in range(0, len(bits_filtered), 8):
        if i + 8 <= len(bits_filtered):
            byte_val = sum(bits_filtered[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"\n[Pattern: b1=1 and b2=1] {len(bits_filtered)} bits extracted")
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        flag_section = result[idx:idx+200]
        print(f"  Found Kaal{{: {flag_section}")
        if '}' in flag_section:
            end_idx = flag_section.index('}')
            potential_flag = flag_section[:end_idx+1]
            if len(potential_flag) < 100:
                print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Pattern 2: Extract bit 0 only where bits 0,1,2 are all the same
bits_filtered = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    b0 = (int_repr >> 0) & 1
    b1 = (int_repr >> 1) & 1
    b2 = (int_repr >> 2) & 1
    
    # Only include when all three bits are the same
    if b0 == b1 == b2:
        bits_filtered.append(b0)

if len(bits_filtered) >= 8:
    extracted = []
    for i in range(0, len(bits_filtered), 8):
        if i + 8 <= len(bits_filtered):
            byte_val = sum(bits_filtered[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"\n[Pattern: b0=b1=b2] {len(bits_filtered)} bits extracted")
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        flag_section = result[idx:idx+200]
        print(f"  Found Kaal{{: {flag_section}")
        if '}' in flag_section:
            end_idx = flag_section.index('}')
            potential_flag = flag_section[:end_idx+1]
            if len(potential_flag) < 100:
                print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Pattern 3: Majority voting - take the majority bit value from bits 0,1,2
bits_filtered = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    b0 = (int_repr >> 0) & 1
    b1 = (int_repr >> 1) & 1
    b2 = (int_repr >> 2) & 1
    
    # Majority vote
    vote = b0 + b1 + b2
    bits_filtered.append(1 if vote >= 2 else 0)

extracted = []
for i in range(0, len(bits_filtered), 8):
    if i + 8 <= len(bits_filtered):
        byte_val = sum(bits_filtered[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')
print(f"\n[Pattern: Majority vote of bits 0,1,2]")
if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+200]
    print(f"  Found Kaal{{: {flag_section}")
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100:
            print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Pattern 4: XOR of bits 0,1,2
bits_filtered = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    b0 = (int_repr >> 0) & 1
    b1 = (int_repr >> 1) & 1
    b2 = (int_repr >> 2) & 1
    
    # XOR all three
    bits_filtered.append(b0 ^ b1 ^ b2)

extracted = []
for i in range(0, len(bits_filtered), 8):
    if i + 8 <= len(bits_filtered):
        byte_val = sum(bits_filtered[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')
print(f"\n[Pattern: XOR of bits 0,1,2]")
if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+200]
    print(f"  Found Kaal{{: {flag_section}")
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100:
            print(f"\n  POTENTIAL FLAG: {potential_flag}")

print("\n[*] Done")
