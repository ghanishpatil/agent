#!/usr/bin/env python3
"""
Extract message from head.weight tensor
Previous analysis found "signals in alignment will wake it" there
"""

import onnx
import struct

model = onnx.load("challenge_final (2).onnx")

# Get head.weight
head_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "head.weight":
        head_tensor = tensor
        break

if not head_tensor:
    print("[-] head.weight not found")
    exit(1)

raw_data = head_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

print(f"[*] head.weight has {num_floats} floats")

# Try all bit positions
for bit_pos in range(32):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append((int_repr >> bit_pos) & 1)
    
    # Convert to bytes
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    # Look for readable text
    if 'signal' in result.lower() or 'align' in result.lower() or 'wake' in result.lower():
        print(f"\n[*] Bit {bit_pos} contains message:")
        print(result)
        print()

# Also try LSB extraction and show all readable fragments
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

print(f"\n[*] LSB extraction from head.weight:")
print(f"[*] Total bytes: {len(extracted)}")
print(f"[*] Content: {result}")

# Look for any Kaal{ flags
if 'Kaal{' in result:
    start = result.index('Kaal{')
    end = result.find('}', start)
    if end != -1:
        print(f"\n[+] FLAG FOUND: {result[start:end+1]}")

print("\n[*] Done")
