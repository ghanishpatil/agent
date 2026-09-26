#!/usr/bin/env python3
"""
Extract ALL readable text fragments from fc1 LSB
Look for more clues about how to find the flag
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

result = bytes(extracted).decode('latin-1', errors='ignore')

# Find all readable text fragments (10+ consecutive printable chars)
current = ""
fragments = []

for i, c in enumerate(result):
    if 32 <= ord(c) < 127:
        current += c
    else:
        if len(current) >= 10:
            fragments.append((i - len(current), current))
        current = ""

if current and len(current) >= 10:
    fragments.append((len(result) - len(current), current))

print(f"[*] Found {len(fragments)} readable fragments (10+ chars)\n")

# Look for fragments containing keywords
keywords = ['whisper', 'signal', 'chord', 'sparse', 'align', 'trigger', 'wait', 'fc2', 'right', 'few', 'silence', 'ear', 'reveal']

print("[*] Fragments containing keywords:")
for offset, frag in fragments:
    lower_frag = frag.lower()
    for kw in keywords:
        if kw in lower_frag:
            print(f"\n  Offset {offset}: '{frag}'")
            break

# Also look for any fragments that might be instructions
print("\n\n[*] All fragments over 30 chars (might contain instructions):")
for offset, frag in fragments:
    if len(frag) > 30:
        print(f"\n  Offset {offset}: {frag}")

print("\n[*] Done")
