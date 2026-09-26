#!/usr/bin/env python3
"""
"c2; only the right few signals"
What if "right" means the right-most bits (MSB, high-order bits)?
Try extracting from fc2 using high-order bits instead of LSB
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

# Try extracting from high-order bits (bits 24-31, the "right" side when viewing as binary)
for bit_pos in range(24, 32):
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
            print(f"\n[+] FLAG FOUND at bit {bit_pos}: {flag}")
            break
    
    # Check readability
    readable = sum(1 for c in result if 32 <= ord(c) < 127)
    if readable > len(result) * 0.4:
        print(f"[*] Bit {bit_pos}: {readable}/{len(result)} readable chars")
        if readable > 100:
            print(f"    First 200 chars: {result[:200]}")

# Also try extracting multiple high bits together
print(f"\n[*] Trying to extract 2 high bits per float...")
bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    # Extract bits 30 and 31
    bits.append((int_repr >> 30) & 1)
    bits.append((int_repr >> 31) & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

if 'Kaal{' in result:
    start = result.index('Kaal{')
    end = result.find('}', start)
    if end != -1:
        print(f"[+] FLAG FOUND with 2 high bits: {result[start:end+1]}")
else:
    readable = sum(1 for c in result if 32 <= ord(c) < 127)
    print(f"[-] No flag. Readable: {readable}/{len(result)}")

print("\n[*] Done")
