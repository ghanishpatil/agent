#!/usr/bin/env python3
"""
Extract from fc2.weight - "the last whisper waits at fc2"
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

# Get fc2.weight
fc2_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc2.weight":
        fc2_tensor = tensor
        break

if not fc2_tensor:
    print("[-] fc2.weight not found")
    exit(1)

raw_data = fc2_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

print(f"[*] fc2.weight has {num_floats} floats ({len(raw_data)} bytes)")

# Try all bit positions
print("\n[*] Extracting from all bit positions...")

for bit_pos in range(8):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append((int_repr >> bit_pos) & 1)
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    # Look for Kaal{
    if 'Kaal{' in result:
        print(f"\n[Bit {bit_pos}] Found Kaal{{:")
        idx = result.index('Kaal{')
        flag_section = result[idx:idx+200]
        print(f"  {repr(flag_section)}")
        
        if '}' in flag_section:
            end_idx = flag_section.index('}')
            potential_flag = flag_section[:end_idx+1]
            if len(potential_flag) < 100:
                printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
                if printable_count / len(potential_flag) > 0.9:
                    print(f"\n  CLEAN FLAG: {potential_flag}")

print("\n[*] Done")
