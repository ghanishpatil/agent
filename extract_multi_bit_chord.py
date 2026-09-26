#!/usr/bin/env python3
"""
"Chord" = multiple bits together
Extract multiple LSBs at once from fc1
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

print(f"[*] fc1.weight has {num_floats} floats")

# Try extracting 2, 3, 4 bits per float (chord = multiple bits)
for num_bits in [2, 3, 4]:
    print(f"\n[*] Trying {num_bits} bits per float...")
    
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        # Extract num_bits LSBs
        for bit_pos in range(num_bits):
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
            print(f"[+] FLAG FOUND with {num_bits} bits: {flag}")
            break
    else:
        # Check first occurrence of readable text
        readable_start = -1
        for i in range(len(result) - 100):
            chunk = result[i:i+100]
            readable = sum(1 for c in chunk if 32 <= ord(c) < 127)
            if readable > 80:
                readable_start = i
                break
        
        if readable_start >= 0:
            print(f"    Found readable section at offset {readable_start}")
            print(f"    Sample: {result[readable_start:readable_start+200]}")

print("\n[*] Done")
