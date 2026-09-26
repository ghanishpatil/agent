#!/usr/bin/env python3
"""
Extract full message from head.weight tensor
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

# Get head.weight
head_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "head.weight":
        head_tensor = tensor
        break

if not head_tensor:
    print("[-] head.weight not found")
    exit(1)

raw_data = head_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

print(f"[*] head.weight has {num_floats} floats ({len(raw_data)} bytes)")

# Extract LSB
print("\n[*] Extracting LSB...")
bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append(int_repr & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')
print(f"\nFull extraction:\n{result}\n")

# Try all bit positions
print("\n[*] Trying all bit positions...")
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
    
    # Look for readable text or flag
    if 'Kaal{' in result or 'alignment' in result or 'chord' in result or 'sparse' in result:
        print(f"\n[Bit {bit_pos}]:")
        print(result)

print("\n[*] Done")
