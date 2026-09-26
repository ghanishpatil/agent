#!/usr/bin/env python3
"""
Use fc2 as a one-time pad / XOR key for fc1
"""

import onnx
import struct
import re

model = onnx.load("challenge_final (2).onnx")

# Get fc1 and fc2
fc1_data = None
fc2_data = None

for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        fc1_data = struct.unpack(f'{num_floats}f', raw)
    elif tensor.name == "fc2.weight":
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        fc2_data = struct.unpack(f'{num_floats}f', raw)

print(f"[*] fc1: {len(fc1_data)} floats")
print(f"[*] fc2: {len(fc2_data)} floats")

# Extract LSB from fc1
def get_lsb_bytes(floats):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append(int_repr & 1)
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    return bytes(extracted)

fc1_bytes = get_lsb_bytes(fc1_data)

# Use fc2 FLOAT VALUES as XOR key (convert to bytes)
print(f"\n[*] Using fc2 float values as XOR key...")

# Convert fc2 floats to bytes (take integer part modulo 256)
fc2_key = bytes([int(abs(f) * 255) % 256 for f in fc2_data])

print(f"[*] fc2 key length: {len(fc2_key)} bytes")

# XOR fc1 with fc2 key (repeating)
xored = bytearray()
for i in range(min(len(fc1_bytes), 100000)):  # First 100KB
    xored.append(fc1_bytes[i] ^ fc2_key[i % len(fc2_key)])

result = bytes(xored).decode('latin-1', errors='ignore')

# Look for clean flags
for match in re.finditer(r'Kaal\{[^\}]{10,150}\}', result):
    flag = match.group()
    if all(32 <= ord(c) < 127 for c in flag):
        if 'surface_flag' not in flag and 'l4yers_of_d3c03pt10n' not in flag:
            print(f"\n[+] CLEAN FLAG FOUND: {flag}")

print("\n[*] Done")
