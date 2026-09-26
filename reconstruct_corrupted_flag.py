#!/usr/bin/env python3
"""
Reconstruct the corrupted flag from fc1.weight
The challenge might be about fixing the corruption, not finding new data
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

# Find the corrupted flag
if 'Kaal{' in result:
    idx = result.index('Kaal{')
    # Extract a large section
    flag_section = result[idx:idx+500]
    
    print("[*] Corrupted flag section:")
    print(repr(flag_section))
    
    # Try to find the pattern
    # We know from Spider challenge it was: Kaal{l4yers_of_d3c03pt10n_m@sk_7h3_pr353nc3_0f_pO1s0ns}
    # Maybe this challenge has a similar pattern but different corruption
    
    print("\n[*] Analyzing corruption pattern...")
    
    # Find where corruption starts
    clean_start = "Kaal{l4yers_of_d3c03pt10n_m"
    if clean_start in flag_section:
        corruption_start = len(clean_start)
        print(f"  Corruption starts at position {corruption_start}")
        print(f"  Before corruption: {flag_section[:corruption_start]}")
        
        # Find where it becomes clean again
        # Look for common flag patterns
        remaining = flag_section[corruption_start:]
        print(f"\n  Corrupted section (first 200 chars):")
        print(f"  {repr(remaining[:200])}")
        
        # Try to find readable parts in the corruption
        readable_parts = []
        current_readable = ""
        for c in remaining:
            if 32 <= ord(c) < 127 and c not in '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f':
                current_readable += c
            else:
                if len(current_readable) > 3:
                    readable_parts.append(current_readable)
                current_readable = ""
        
        if current_readable and len(current_readable) > 3:
            readable_parts.append(current_readable)
        
        print(f"\n  Readable parts in corruption:")
        for part in readable_parts[:10]:
            print(f"    {part}")

# Also check if there's a HDWGT3 or FINAL marker
print("\n[*] Looking for new markers...")
for marker in ['HDWGT2', 'HDWGT3', 'FINAL', 'CHORD', 'SPARSE', 'WHISPER']:
    if marker in result:
        idx = result.index(marker)
        print(f"\n  Found {marker}:")
        print(f"  {result[idx:idx+300]}")

print("\n[*] Done")
