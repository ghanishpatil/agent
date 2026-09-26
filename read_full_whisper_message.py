#!/usr/bin/env python3
"""
Read the full whisper message from fc1 LSB to understand the clue better
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

# Find "the last whisper" and extract everything around it
if 'the last whisper' in result:
    idx = result.index('the last whisper')
    print(f"[*] Found 'the last whisper' at offset {idx}")
    
    # Extract 5000 chars before and after
    start = max(0, idx - 1000)
    end = min(len(result), idx + 5000)
    section = result[start:end]
    
    # Clean up and show
    print(f"\n[*] Context around 'the last whisper':")
    print("=" * 80)
    
    # Show with markers for non-printable
    output = ""
    for c in section:
        if 32 <= ord(c) < 127:
            output += c
        elif c == '\n':
            output += '\n'
        elif c == '\t':
            output += '\t'
        else:
            output += f'[{ord(c):02x}]'
    
    print(output)
    print("=" * 80)

# Also search for other keywords
keywords = ['fc2', 'signal', 'chord', 'sparse', 'align', 'trigger', 'whisper', 'wait']
print(f"\n[*] Searching for keywords...")
for kw in keywords:
    if kw in result.lower():
        idx = result.lower().index(kw)
        context = result[max(0, idx-50):min(len(result), idx+100)]
        # Clean
        clean = ""
        for c in context:
            if 32 <= ord(c) < 127:
                clean += c
            else:
                clean += '.'
        print(f"  '{kw}' at {idx}: ...{clean}...")

print("\n[*] Done")
