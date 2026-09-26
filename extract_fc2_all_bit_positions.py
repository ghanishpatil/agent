#!/usr/bin/env python3
"""
Extract from fc2.weight using different bit positions
"only the right few signals" might mean a specific bit position
"""

import onnx
import struct

model = onnx.load("challenge_final (2).onnx")

# Get fc2.weight
fc2_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc2.weight":
        fc2_tensor = tensor
        break

raw_data = fc2_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

print(f"[*] fc2.weight has {num_floats} floats")

# Try each bit position 0-31
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
    
    # Look for flag
    if 'Kaal{' in result:
        start = result.index('Kaal{')
        end = result.find('}', start)
        if end != -1:
            flag = result[start:end+1]
            print(f"\n[+] FLAG FOUND at bit position {bit_pos}: {flag}")
            break
    
    # Also check for readable text
    readable_count = sum(1 for c in result if 32 <= ord(c) < 127)
    if readable_count > len(result) * 0.5:  # More than 50% readable
        print(f"[*] Bit {bit_pos}: {readable_count}/{len(result)} readable chars")
        if readable_count > 1000:
            print(f"    First 200 chars: {result[:200]}")

print("\n[*] Done")
