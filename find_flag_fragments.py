#!/usr/bin/env python3
"""
Look for flag fragments like "9{7", "R:{", "c}k" and try to reconstruct
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

# Search for patterns that look like flag parts
patterns = ['{', '}', 'K4', 'k4', 'Kaal', 'kaal']

print("[*] Searching for flag-like patterns after 'the last whisper'...\n")

if 'the last whisper' in result:
    idx = result.index('the last whisper')
    section = result[idx:idx+10000]
    
    # Look for any occurrence of { or }
    for i, c in enumerate(section):
        if c in '{}':
            # Extract context around it
            start = max(0, i-20)
            end = min(len(section), i+20)
            context = section[start:end]
            
            # Show printable version
            printable = ''.join(ch if 32 <= ord(ch) < 127 else '.' for ch in context)
            print(f"Position {i}: ...{printable}...")
            
            if i < 100:  # Only show first few
                print(f"  Raw: {repr(context)}\n")

print("\n[*] Done")
