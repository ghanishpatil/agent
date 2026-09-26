#!/usr/bin/env python3
"""
Final Whisper - Extract multiple bits per float (chord = multiple signals)
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

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

# Try extracting 2 bits per float (bits 0 and 1)
print("\n[*] Extracting 2 bits per float (LSB and bit 1)...")
bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append((int_repr >> 0) & 1)
    bits.append((int_repr >> 1) & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')
if 'Kaal{' in result:
    print(f"\n[2-bit extraction] Found Kaal{{:")
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+200]
    print(f"  {flag_section}")
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100 and potential_flag.count('{') == 1:
            print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Try extracting 3 bits per float (bits 0, 1, 2)
print("\n[*] Extracting 3 bits per float (bits 0-2)...")
bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append((int_repr >> 0) & 1)
    bits.append((int_repr >> 1) & 1)
    bits.append((int_repr >> 2) & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')
if 'Kaal{' in result:
    print(f"\n[3-bit extraction] Found Kaal{{:")
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+200]
    print(f"  {flag_section}")
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100 and potential_flag.count('{') == 1:
            print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Try extracting 4 bits per float (lower nibble)
print("\n[*] Extracting 4 bits per float (lower nibble)...")
bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    for bit_pos in range(4):
        bits.append((int_repr >> bit_pos) & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')
if 'Kaal{' in result:
    print(f"\n[4-bit extraction] Found Kaal{{:")
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+200]
    print(f"  {flag_section}")
    if '}' in flag_section:
        end_idx = flag_section.index('}')
        potential_flag = flag_section[:end_idx+1]
        if len(potential_flag) < 100 and potential_flag.count('{') == 1:
            print(f"\n  POTENTIAL FLAG: {potential_flag}")

# Try different bit combinations
print("\n[*] Trying different bit position combinations...")
for combo in [(0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (0, 1, 3), (0, 2, 3)]:
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        for bit_pos in combo:
            bits.append((int_repr >> bit_pos) & 1)
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    if 'Kaal{' in result and 'HDWGT' not in result:
        print(f"\n[Bits {combo}] Found clean Kaal{{:")
        idx = result.index('Kaal{')
        flag_section = result[idx:idx+200]
        print(f"  {flag_section}")
        if '}' in flag_section:
            end_idx = flag_section.index('}')
            potential_flag = flag_section[:end_idx+1]
            if len(potential_flag) < 100 and potential_flag.count('{') == 1:
                print(f"\n  POTENTIAL FLAG: {potential_flag}")

print("\n[*] Done")
