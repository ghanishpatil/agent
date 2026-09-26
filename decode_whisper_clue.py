#!/usr/bin/env python3
"""
Decode the whisper clue more carefully
"""

import onnx
import struct

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

# Find all readable text fragments
if 'the last whisper' in result:
    idx = result.index('the last whisper')
    
    # Extract a larger section
    section = result[idx:idx+2000]
    
    # Find all sequences of printable ASCII (5+ chars)
    current = ""
    fragments = []
    
    for c in section:
        if 32 <= ord(c) < 127:
            current += c
        else:
            if len(current) >= 5:
                fragments.append(current)
            current = ""
    
    if current and len(current) >= 5:
        fragments.append(current)
    
    print("[*] Readable fragments in whisper message:")
    for i, frag in enumerate(fragments[:20]):
        print(f"  {i+1}. {frag}")

print("\n[*] Done")
