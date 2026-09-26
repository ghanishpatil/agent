#!/usr/bin/env python3
"""
Find all occurrences of the structure marker pattern
b7 29 5a c1 01 XX 05 1c
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

# Search for pattern b7 29 5a c1 01
pattern = b'\xb7\x29\x5a\xc1\x01'

print(f"[*] Searching for structure markers...")

offset = 0
markers = []
while True:
    idx = result.find(pattern, offset)
    if idx == -1:
        break
    
    # Get the next few bytes
    section = result[idx:idx+20]
    markers.append((idx, section))
    offset = idx + 1

print(f"[*] Found {len(markers)} markers\n")

for i, (offset, section) in enumerate(markers):
    hex_str = ' '.join(f'{b:02x}' for b in section)
    print(f"  {i+1}. Offset {offset}: {hex_str}")
    
    # Try to extract text after marker
    text_start = offset + 8  # Skip marker bytes
    text_section = result[text_start:text_start+100]
    
    # Extract readable text
    readable = ''
    for b in text_section:
        if 32 <= b < 127:
            readable += chr(b)
        else:
            break
    
    if len(readable) > 5:
        print(f"     Text: {readable}")
    print()

# Check if there's a marker 04 (since we have 00, 01, 02, 03)
print(f"\n[*] Looking for marker with 04...")
pattern_04 = b'\xb7\x29\x5a\xc1\x01\x04\x05\x1c'
if pattern_04 in result:
    idx = result.index(pattern_04)
    print(f"[+] Found marker 04 at offset {idx}!")
    text_section = result[idx+8:idx+200]
    readable = ''.join(chr(b) if 32 <= b < 127 else f'[{b:02x}]' for b in text_section)
    print(f"    Content: {readable}")
else:
    print(f"[-] No marker 04 found")

print("\n[*] Done")
