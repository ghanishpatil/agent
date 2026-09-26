#!/usr/bin/env python3
"""
Extract where bits form a "chord" - specific bit patterns
A chord in music = multiple notes together = multiple bits set
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

# Strategy 1: Extract from positions where bits 0,1,2 are ALL 1 (full chord)
print("\n[*] Extracting where bits 0,1,2 are all 1 (full chord)...")

chord_bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    b0 = (int_repr >> 0) & 1
    b1 = (int_repr >> 1) & 1
    b2 = (int_repr >> 2) & 1
    
    # Only include if all three bits are 1
    if b0 == 1 and b1 == 1 and b2 == 1:
        # Extract a higher bit as the data
        b3 = (int_repr >> 3) & 1
        chord_bits.append(b3)

if len(chord_bits) >= 8:
    extracted = []
    for i in range(0, len(chord_bits), 8):
        if i + 8 <= len(chord_bits):
            byte_val = sum(chord_bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"  Extracted {len(extracted)} bytes from {len(chord_bits)} chord positions")
    
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        flag_section = result[idx:idx+150]
        print(f"\n  FOUND FLAG: {flag_section}")
        
        if '}' in flag_section:
            end_idx = flag_section.index('}')
            potential_flag = flag_section[:end_idx+1]
            if len(potential_flag) < 100:
                printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
                if printable_count / len(potential_flag) > 0.9:
                    print(f"\n  CLEAN FLAG: {potential_flag}")

# Strategy 2: Extract where bits 0,1,2 are ALL 0 (silence/sparse)
print("\n[*] Extracting where bits 0,1,2 are all 0 (silence)...")

silence_bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    b0 = (int_repr >> 0) & 1
    b1 = (int_repr >> 1) & 1
    b2 = (int_repr >> 2) & 1
    
    # Only include if all three bits are 0 (sparse/silence)
    if b0 == 0 and b1 == 0 and b2 == 0:
        # Extract a higher bit as the data
        b3 = (int_repr >> 3) & 1
        silence_bits.append(b3)

if len(silence_bits) >= 8:
    extracted = []
    for i in range(0, len(silence_bits), 8):
        if i + 8 <= len(silence_bits):
            byte_val = sum(silence_bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"  Extracted {len(extracted)} bytes from {len(silence_bits)} silence positions")
    
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        flag_section = result[idx:idx+150]
        print(f"\n  FOUND FLAG: {flag_section}")
        
        if '}' in flag_section:
            end_idx = flag_section.index('}')
            potential_flag = flag_section[:end_idx+1]
            if len(potential_flag) < 100:
                printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
                if printable_count / len(potential_flag) > 0.9:
                    print(f"\n  CLEAN FLAG: {potential_flag}")

print("\n[*] Done")
