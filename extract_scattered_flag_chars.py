#!/usr/bin/env python3
"""
Extract characters around { and } to reconstruct scattered flag
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

result = bytes(extracted).decode('latin-1', errors='ignore')

# Find "the last whisper" section
if 'the last whisper' in result:
    idx = result.index('the last whisper')
    section = result[idx:idx+2000]
    
    print("[*] Looking for scattered flag characters...\n")
    
    # Find all { and } positions and extract nearby printable chars
    flag_chars = []
    
    for i, c in enumerate(section):
        if c in '{}':
            # Look at characters before and after
            for offset in range(-5, 6):
                pos = i + offset
                if 0 <= pos < len(section):
                    ch = section[pos]
                    if 32 <= ord(ch) < 127 and ch not in '\x00\x01\x02\x03\x04\x05':
                        if offset == 0:
                            print(f"Position {i}: '{ch}' (the bracket itself)")
                        else:
                            print(f"Position {i}: offset {offset:+d} = '{ch}'")
    
    # Try a different approach - look for "Kaal" pattern
    print("\n[*] Searching for 'Kaal' or 'K44l' or similar patterns...")
    
    for i in range(len(section) - 4):
        substr = section[i:i+4]
        # Check if it could be "Kaal" with some corruption
        if 'K' in substr or 'k' in substr:
            printable = ''.join(ch if 32 <= ord(ch) < 127 else '.' for ch in substr)
            if printable.count('.') < 3:  # At least 2 printable chars
                context = section[max(0,i-10):i+20]
                printable_context = ''.join(ch if 32 <= ord(ch) < 127 else '.' for ch in context)
                if '{' in context or '}' in context:
                    print(f"  Position {i}: {printable} in context: {printable_context}")

print("\n[*] Done")
