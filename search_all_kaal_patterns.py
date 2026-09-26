#!/usr/bin/env python3
"""
Search for ALL occurrences of "Kaal{" in fc1 LSB data
Maybe there are multiple flags and I found the wrong one
"""

import onnx
import struct
import re

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

print(f"[*] Total extracted: {len(result)} bytes")

# Find ALL occurrences of "Kaal{"
pattern = r'Kaal\{[^}]*\}'
matches = list(re.finditer(pattern, result))

print(f"\n[*] Found {len(matches)} potential flags:")
for i, match in enumerate(matches):
    flag = match.group()
    pos = match.start()
    print(f"\n  {i+1}. At offset {pos}:")
    print(f"     {flag}")
    
    # Show context
    context_start = max(0, pos - 50)
    context_end = min(len(result), pos + len(flag) + 50)
    context = result[context_start:context_end]
    
    # Clean context for display
    clean_context = ""
    for c in context:
        if 32 <= ord(c) < 127:
            clean_context += c
        else:
            clean_context += f'[{ord(c):02x}]'
    
    print(f"     Context: ...{clean_context}...")

# Also search for partial matches
print(f"\n[*] Searching for 'Kaal{{' without closing brace...")
kaal_starts = [m.start() for m in re.finditer(r'Kaal\{', result)]
print(f"[*] Found {len(kaal_starts)} occurrences of 'Kaal{{'")

for pos in kaal_starts[:10]:  # Show first 10
    # Extract next 100 chars
    section = result[pos:pos+100]
    clean = ""
    for c in section:
        if 32 <= ord(c) < 127:
            clean += c
        else:
            clean += f'[{ord(c):02x}]'
    print(f"  At {pos}: {clean}")

print("\n[*] Done")
