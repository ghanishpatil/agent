#!/usr/bin/env python3
"""
Step-by-step solve from scratch
"""

import onnx
import struct

print("="*80)
print("STEP 1: Load ONNX and extract LSB from fc1.weight")
print("="*80)

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

print(f"[*] fc1.weight has {num_floats} floats")

# Extract LSB (bit 0)
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

result = bytes(extracted)

print(f"[*] Extracted {len(result)} bytes from LSB")

print("\n" + "="*80)
print("STEP 2: Find structure markers")
print("="*80)

# Find marker pattern b7 29 5a c1 01
pattern = b'\xb7\x29\x5a\xc1\x01'
markers = []
offset = 0
while True:
    idx = result.find(pattern, offset)
    if idx == -1:
        break
    markers.append(idx)
    offset = idx + 1

print(f"[*] Found {len(markers)} markers at offsets: {markers}")

print("\n" + "="*80)
print("STEP 3: Extract flag sections from markers")
print("="*80)

# Markers are at: 512, 768, 1024, 1280
# Marker 0 (512): Contains start of flag
# Marker 1 (768): Contains end of flag

marker0_section = result[512+8:768]
marker1_section = result[768+8:1024]

print(f"\n[*] Marker 0 section (first 60 bytes):")
print(f"Hex: {marker0_section[:60].hex()}")
print(f"ASCII: {marker0_section[:60]}")

print(f"\n[*] Marker 1 section (first 60 bytes):")
print(f"Hex: {marker1_section[:60].hex()}")
print(f"ASCII: {marker1_section[:60]}")

print("\n" + "="*80)
print("STEP 4: Identify the flag parts")
print("="*80)

# Find Kaal{ in marker 0
kaal_start = marker0_section.find(b'Kaal{')
if kaal_start >= 0:
    # Extract readable part
    flag_part1 = b'Kaal{l4yers_of_d3c03pt10n_m'
    print(f"[*] Marker 0 contains: {flag_part1}")
    
    # Position after 'm'
    m_pos = kaal_start + len(flag_part1)
    print(f"[*] After 'm' at position {m_pos}, bytes are: {marker0_section[m_pos:m_pos+10].hex()}")

# Find ending in marker 1
if b'@sk_7h3_pr353nc3_0f_pO1s0ns}' in marker1_section:
    print(f"[*] Marker 1 contains: @sk_7h3_pr353nc3_0f_pO1s0ns}}")
    
    # What's before @sk?
    ask_pos = marker1_section.find(b'@sk')
    print(f"[*] Before '@sk' at position {ask_pos}, bytes are: {marker1_section[max(0,ask_pos-10):ask_pos].hex()}")

print("\n" + "="*80)
print("STEP 5: Analyze the corruption")
print("="*80)

# The flag should be: Kaal{l4yers_of_d3c03pt10n_m???@sk_7h3_pr353nc3_0f_pO1s0ns}
# Between 'm' and '@sk' there's corruption

# Let me check the EXACT bytes
print(f"\n[*] Checking exact bytes in marker 0 after 'm':")
for i in range(m_pos, min(m_pos + 20, len(marker0_section))):
    b = marker0_section[i]
    if 32 <= b < 127:
        print(f"  Position {i}: 0x{b:02x} = '{chr(b)}'")
    else:
        print(f"  Position {i}: 0x{b:02x} = [non-printable]")

print(f"\n[*] Checking exact bytes in marker 1 before '@sk':")
for i in range(max(0, ask_pos - 10), ask_pos):
    b = marker1_section[i]
    if 32 <= b < 127:
        print(f"  Position {i}: 0x{b:02x} = '{chr(b)}'")
    else:
        print(f"  Position {i}: 0x{b:02x} = [non-printable]")

print("\n" + "="*80)
print("STEP 6: Try to reconstruct the flag")
print("="*80)

# The pattern suggests: m + ? + @sk
# Common words: mask, m@sk
# Let me try different reconstructions

attempts = [
    "Kaal{l4yers_of_d3c03pt10n_m@sk_7h3_pr353nc3_0f_pO1s0ns}",
    "Kaal{l4yers_of_d3c03pt10n_mask_7h3_pr353nc3_0f_pO1s0ns}",
    "Kaal{l4yers_of_d3c03pt10n_m4sk_7h3_pr353nc3_0f_pO1s0ns}",
]

print("[*] Possible flag reconstructions:")
for i, flag in enumerate(attempts, 1):
    print(f"  {i}. {flag}")

print("\n[*] Done - analyze the output above")
