#!/usr/bin/env python3
"""
Extract the EXACT bytes of the flag sections
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

# Find the exact flag bytes
marker0 = result[512+8:768]
marker1 = result[768+8:1024]

# Find Kaal{ in marker 0
kaal_pos = marker0.find(b'Kaal{')
if kaal_pos >= 0:
    # Extract 60 bytes from Kaal{
    flag_section = marker0[kaal_pos:kaal_pos+60]
    
    print("[*] Marker 0 flag section (60 bytes):")
    print(f"Hex: {flag_section.hex()}")
    print(f"Bytes: {list(flag_section)}")
    print(f"ASCII: {flag_section}")
    
    # Show character by character
    print(f"\n[*] Character by character:")
    for i, b in enumerate(flag_section):
        if 32 <= b < 127:
            print(f"  {i:2d}: 0x{b:02x} = '{chr(b)}'")
        else:
            print(f"  {i:2d}: 0x{b:02x} = [non-printable]")

# Find the ending in marker 1
print(f"\n\n[*] Marker 1 first 60 bytes:")
flag_section1 = marker1[:60]
print(f"Hex: {flag_section1.hex()}")
print(f"Bytes: {list(flag_section1)}")

print(f"\n[*] Character by character:")
for i, b in enumerate(flag_section1):
    if 32 <= b < 127:
        print(f"  {i:2d}: 0x{b:02x} = '{chr(b)}'")
    else:
        print(f"  {i:2d}: 0x{b:02x} = [non-printable]")

# Now let's see what the ACTUAL missing bytes should be
# The flag should be: Kaal{l4yers_of_d3c03pt10n_m???@sk_7h3_pr353nc3_0f_pO1s0ns}
# Position 27 is 'm', then corruption, then '@sk' starts

print(f"\n\n[*] Analysis:")
print(f"Position 27 in marker 0: 'm' (0x{marker0[kaal_pos+27]:02x})")
print(f"Next bytes: {marker0[kaal_pos+28:kaal_pos+35].hex()}")

# Check if marker 1 really starts with '@sk' or something else
if marker1[3:6] == b'@sk':
    print(f"\n[*] Marker 1 position 3-5: '@sk' confirmed")
else:
    print(f"\n[*] Marker 1 position 3-5: {marker1[3:6]} = {marker1[3:6].hex()}")

print("\n[*] Done")
