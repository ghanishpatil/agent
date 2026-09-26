#!/usr/bin/env python3
"""
Check what comes after marker 3
Maybe there's more data
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

# Marker 3 is at offset 1280
# Check next 1000 bytes
section = result[1280+256:1280+1256]

print("[*] Data after marker 3:")
print(f"[*] Hex: {section[:200].hex()}")

# Look for readable text
readable = ''
for b in section:
    if 32 <= b < 127:
        readable += chr(b)
    else:
        readable += f'[{b:02x}]'

print(f"\n[*] ASCII: {readable[:500]}")

# Search for any Kaal{ in the rest of the data
rest = result[1536:]
if b'Kaal{' in rest:
    idx = rest.index(b'Kaal{')
    print(f"\n[+] Found 'Kaal{{' at offset {1536 + idx}")
    flag_section = rest[idx:idx+200]
    print(f"    Content: {flag_section}")

print("\n[*] Done")
