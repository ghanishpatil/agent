#!/usr/bin/env python3
"""
New interpretation:
"the last whisper waits at fc2" = data is IN fc2
"only the right few signals" = use head to select which fc2 positions
"signals in alignment will wake it" = head tells us which signals to extract
"""

import onnx
import struct

model = onnx.load("challenge_final (2).onnx")

# Get fc2 and head
fc2_data = None
head_data = None

for tensor in model.graph.initializer:
    if tensor.name == "fc2.weight":
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        fc2_data = struct.unpack(f'{num_floats}f', raw)
    elif tensor.name == "head.weight":
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        head_data = struct.unpack(f'{num_floats}f', raw)

print(f"[*] fc2.weight: {len(fc2_data)} floats")
print(f"[*] head.weight: {len(head_data)} floats")

# Get LSB from head to use as selector
def get_lsb_bits(floats):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append(int_repr & 1)
    return bits

head_bits = get_lsb_bits(head_data)

# Find positions where head LSB=1
selected_positions = [i for i, bit in enumerate(head_bits) if bit == 1]
print(f"\n[*] Head has {len(selected_positions)} positions with LSB=1")
print(f"[*] Selected positions: {selected_positions[:50]}")

# Now extract from fc2 at these positions (with wrapping)
print(f"\n[*] Extracting from fc2 at head-selected positions...")

# Try different bit positions in fc2
for bit_pos in range(8):  # Try bits 0-7
    bits = []
    for pos in selected_positions:
        fc2_pos = pos % len(fc2_data)  # Wrap around
        int_repr = struct.unpack('I', struct.pack('f', fc2_data[fc2_pos]))[0]
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
    if readable > len(result) * 0.3:
        print(f"[*] Bit {bit_pos}: {readable}/{len(result)} readable")
        if readable > 50:
            print(f"    Sample: {result[:150]}")

print("\n[*] Done")
