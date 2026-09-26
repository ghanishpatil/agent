#!/usr/bin/env python3
"""
Extract the "last whisper" message
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

# Find "the last whisper"
if 'the last whisper' in result:
    idx = result.index('the last whisper')
    message_section = result[idx:idx+500]
    
    print("[*] Found 'the last whisper' message:")
    print(repr(message_section))
    
    # Extract printable characters
    printable = ''.join(c if 32 <= ord(c) < 127 else ' ' for c in message_section)
    print(f"\n[*] Printable version:")
    print(printable)
    
    # Look for any flag-like patterns
    if 'Kaal{' in message_section:
        flag_idx = message_section.index('Kaal{')
        flag_section = message_section[flag_idx:flag_idx+150]
        print(f"\n[*] Found Kaal{{ in message:")
        print(repr(flag_section))

print("\n[*] Done")
