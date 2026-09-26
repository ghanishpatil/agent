#!/usr/bin/env python3
"""
Try extracting from conv2 tensor - the clue says "c2; only the right few signals"
Maybe c2 = conv2, and we extract LSB from there
"""

import onnx
import struct

model = onnx.load("challenge_final (2).onnx")

# Get conv2.weight
conv2_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "conv2.weight":
        conv2_tensor = tensor
        break

if not conv2_tensor:
    print("[-] conv2.weight not found")
    exit(1)

raw_data = conv2_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

print(f"[*] conv2.weight has {num_floats} floats")

# Extract LSB
bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append(int_repr & 1)

# Convert to bytes
extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

print(f"[*] Extracted {len(extracted)} bytes")

# Look for flag
if 'Kaal{' in result:
    start = result.index('Kaal{')
    end = result.find('}', start)
    if end != -1:
        flag = result[start:end+1]
        print(f"\n[+] FLAG FOUND: {flag}")
else:
    print(f"\n[*] No Kaal{{ found in conv2")
    print(f"[*] First 500 chars:")
    print(result[:500])
    
    # Show readable fragments
    current = ""
    fragments = []
    for c in result:
        if 32 <= ord(c) < 127:
            current += c
        else:
            if len(current) >= 10:
                fragments.append(current)
            current = ""
    
    if fragments:
        print(f"\n[*] Readable fragments (10+ chars):")
        for frag in fragments[:20]:
            print(f"  {frag}")

print("\n[*] Done")
