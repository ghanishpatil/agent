#!/usr/bin/env python3
"""
Find where at least 3 tensors have sparse weights (chord = 3+ notes)
"""

import onnx
import struct
from collections import Counter

model = onnx.load("challenge_final 2.onnx")

print("[*] Finding chord positions (3+ tensors sparse at same position)...")

# Get all weight tensors
weight_tensors = []
for tensor in model.graph.initializer:
    if tensor.HasField('raw_data') and 'weight' in tensor.name:
        weight_tensors.append(tensor)

# Find sparse positions for each tensor
threshold = 1e-5
all_sparse_positions = []

for tensor in weight_tensors:
    raw_data = tensor.raw_data
    num_floats = len(raw_data) // 4
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    for i, f in enumerate(floats):
        if abs(f) < threshold:
            all_sparse_positions.append(i)

# Count how many tensors have sparse weights at each position
position_counts = Counter(all_sparse_positions)

# Find positions where 3+ tensors are sparse (chord)
chord_positions = [pos for pos, count in position_counts.items() if count >= 3]

print(f"  Found {len(chord_positions)} chord positions (3+ tensors sparse)")

if chord_positions:
    # Extract from fc1.weight at chord positions
    fc1_tensor = None
    for tensor in model.graph.initializer:
        if tensor.name == "fc1.weight":
            fc1_tensor = tensor
            break
    
    if fc1_tensor:
        raw_data = fc1_tensor.raw_data
        num_floats = len(raw_data) // 4
        floats = struct.unpack(f'{num_floats}f', raw_data)
        
        # Extract LSB at chord positions
        chord_bits = []
        for pos in sorted(chord_positions):
            if pos < len(floats):
                int_repr = struct.unpack('I', struct.pack('f', floats[pos]))[0]
                chord_bits.append(int_repr & 1)
        
        # Convert to bytes
        if len(chord_bits) >= 8:
            extracted = []
            for i in range(0, len(chord_bits), 8):
                if i + 8 <= len(chord_bits):
                    byte_val = sum(chord_bits[i+j] << j for j in range(8))
                    extracted.append(byte_val)
            
            result = bytes(extracted).decode('latin-1', errors='ignore')
            print(f"\n[*] Extracted from chord positions:")
            print(f"  First 200 chars: {result[:200]}")
            
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
