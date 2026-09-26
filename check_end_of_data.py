#!/usr/bin/env python3
"""
Check the END of fc1 LSB data for the "final" whisper
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

print(f"[*] Total data: {len(result)} bytes")
print(f"\n[*] Last 2000 bytes:")

# Check last 2000 bytes for readable text
last_section = result[-2000:]

# Convert to readable
readable = ''
for b in last_section:
    if 32 <= b < 127:
        readable += chr(b)
    else:
        readable += f'[{b:02x}]'

print(readable)

# Also search for any Kaal{ in the last section
if b'Kaal{' in last_section:
    idx = last_section.index(b'Kaal{')
    print(f"\n[+] Found Kaal{{ at offset {len(result) - 2000 + idx}")
    flag_section = last_section[idx:idx+200]
    print(f"    Content: {flag_section}")

print("\n[*] Done")
