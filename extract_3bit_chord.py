#!/usr/bin/env python3
"""
Extract 3 LSBs per float as a "chord" (3 bits = 0-7 value)
Then convert to ASCII
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

print(f"[*] Extracting 3-bit chords from {num_floats} floats...")

# Extract 3 LSBs from each float
values = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    # Get bits 0, 1, 2
    three_bit_val = int_repr & 0x07  # 0b111
    values.append(three_bit_val)

print(f"[*] Got {len(values)} 3-bit values")

# Try different interpretations
# 1. Direct mapping to ASCII (add offset)
print("\n[*] Method 1: Map to printable ASCII (add 32)")
result1 = ''.join(chr(v + 32) for v in values[:1000])
if 'Kaal{' in result1:
    print(f"[+] Found flag: {result1[result1.index('Kaal{'):result1.index('Kaal{')+100]}")
else:
    print(f"    Sample: {result1[:200]}")

# 2. Pack 3-bit values into bytes (every 8 values = 3 bytes)
print("\n[*] Method 2: Pack 3-bit values into bytes")
bits = []
for v in values:
    # Add 3 bits
    for i in range(3):
        bits.append((v >> i) & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result2 = bytes(extracted).decode('latin-1', errors='ignore')
if 'Kaal{' in result2:
    import re
    for match in re.finditer(r'Kaal\{[^\}]*\}', result2):
        print(f"[+] Found flag: {match.group()}")
else:
    print(f"    No flag found. Sample: {result2[:200]}")

# 3. Use 3-bit values as indices into alphabet
print("\n[*] Method 3: Map to alphabet subset")
alphabet = "abcdefgh"  # 8 chars for 3-bit values
result3 = ''.join(alphabet[v] for v in values[:1000])
print(f"    Sample: {result3[:200]}")

print("\n[*] Done")
