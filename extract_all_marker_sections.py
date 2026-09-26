#!/usr/bin/env python3
"""
Extract text from all 4 marker sections
"""

import onnx
import struct

model = onnx.load("challenge_final (2).onnx")

# Get fc1.weight
fc1_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
        break

raw_data = fc1_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

# Extract LSB
bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append(int_repr & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted)

# Find all markers
markers = [
    (512, 0),
    (768, 1),
    (1024, 2),
    (1280, 3)
]

print("[*] Extracting sections:\n")

for offset, marker_num in markers:
    # Extract until next marker or 256 bytes
    if marker_num < 3:
        next_offset = markers[marker_num + 1][0]
        section = result[offset+8:next_offset]
    else:
        section = result[offset+8:offset+256]
    
    print(f"=== Marker {marker_num} (offset {offset}) ===")
    
    # Show hex
    print(f"Hex: {section[:100].hex()}")
    
    # Show ASCII
    ascii_str = ''
    for b in section:
        if 32 <= b < 127:
            ascii_str += chr(b)
        else:
            ascii_str += f'[{b:02x}]'
    
    print(f"ASCII: {ascii_str[:200]}")
    print()

# Now try to piece together the flag from markers 0 and 1
print("\n[*] Attempting to reconstruct flag from markers 0 and 1...")

section0 = result[512+8:768]
section1 = result[768+8:1024]

# Extract readable parts
part0 = ''
for b in section0:
    if 32 <= b < 127:
        part0 += chr(b)
    else:
        break

part1 = ''
for b in section1:
    if 32 <= b < 127:
        part1 += chr(b)
    else:
        break

print(f"Part 0: {part0}")
print(f"Part 1: {part1}")

# Try to combine
if part0.startswith('Kaal{') and part1.endswith('}'):
    combined = part0 + part1
    print(f"\n[+] Combined flag: {combined}")
elif 'Kaal{' in part0:
    # Find where it cuts off
    start = part0.index('Kaal{')
    flag_part = part0[start:]
    combined = flag_part + part1
    print(f"\n[+] Reconstructed flag: {combined}")

print("\n[*] Done")
