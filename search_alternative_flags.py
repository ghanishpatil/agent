#!/usr/bin/env python3
"""
Search for alternative flag patterns
"""

import onnx
import struct
import re

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

result = bytes(extracted).decode('latin-1', errors='ignore')

print("[*] Searching for alternative patterns...")

# Search for flag-like patterns
patterns = [
    (r'flag\{[^}]+\}', "flag{...}"),
    (r'FLAG\{[^}]+\}', "FLAG{...}"),
    (r'CTF\{[^}]+\}', "CTF{...}"),
    (r'\{[a-zA-Z0-9_]{20,}\}', "{long_string}"),
    (r'wh1sp3r', "whisper"),
    (r'f1n4l', "final"),
    (r'ch0rd', "chord"),
    (r'sp4rs3', "sparse"),
    (r's1gn4l', "signal"),
]

for pattern, desc in patterns:
    matches = re.findall(pattern, result, re.IGNORECASE)
    if matches:
        print(f"\n[{desc}] Found {len(matches)} matches:")
        for match in matches[:5]:
            print(f"  {match}")

# Also search for the corrupted flag's end to see what comes after
if '@sk_7h3_pr353nc3_0f_pO1s0ns}' in result:
    idx = result.index('@sk_7h3_pr353nc3_0f_pO1s0ns}')
    after_flag = result[idx:idx+300]
    print(f"\n[After corrupted flag]:")
    print(f"  {repr(after_flag)}")

print("\n[*] Done")
