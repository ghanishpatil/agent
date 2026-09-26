#!/usr/bin/env python3
"""
Analyze the exact bytes around the clue messages
Maybe there's a pattern or hidden data
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

# Find the clue messages
clue1 = b"the last whisper waits at f"
clue2 = b"c2; only the right few signa"

if clue1 in result:
    idx1 = result.index(clue1)
    print(f"[*] Clue 1 at offset {idx1}")
    
    # Extract 100 bytes before and after
    section = result[max(0, idx1-100):idx1+len(clue1)+100]
    
    print(f"\n[*] Hex dump around clue 1:")
    for i in range(0, len(section), 16):
        hex_part = ' '.join(f'{b:02x}' for b in section[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in section[i:i+16])
        print(f"  {i:04x}: {hex_part:<48} {ascii_part}")

if clue2 in result:
    idx2 = result.index(clue2)
    print(f"\n\n[*] Clue 2 at offset {idx2}")
    
    # Extract 100 bytes before and after
    section = result[max(0, idx2-100):idx2+len(clue2)+100]
    
    print(f"\n[*] Hex dump around clue 2:")
    for i in range(0, len(section), 16):
        hex_part = ' '.join(f'{b:02x}' for b in section[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in section[i:i+16])
        print(f"  {i:04x}: {hex_part:<48} {ascii_part}")

# Check if there's a pattern in the bytes between the two clues
if clue1 in result and clue2 in result:
    idx1 = result.index(clue1)
    idx2 = result.index(clue2)
    between = result[idx1+len(clue1):idx2]
    
    print(f"\n\n[*] Bytes between clues: {len(between)} bytes")
    print(f"[*] Hex: {between.hex()[:200]}")
    
    # Try to decode as ASCII
    decoded = ''.join(chr(b) if 32 <= b < 127 else f'[{b:02x}]' for b in between[:200])
    print(f"[*] ASCII: {decoded}")

print("\n[*] Done")
