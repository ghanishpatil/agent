#!/usr/bin/env python3
"""
Search fc2 for HDWGT structures or base64 encoded flags
"""

import onnx
import struct
import base64
import re

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
    
    # Look for HDWGT
    if 'HDWGT' in result:
        print(f"\n[+] Found HDWGT at bit position {bit_pos}!")
        idx = result.index('HDWGT')
        section = result[idx:idx+500]
        print(f"    Content: {section}")
        
        # Try to extract base64
        if '|FLAG|' in section:
            parts = section.split('|')
            for i, part in enumerate(parts):
                if part == 'FLAG' and i + 1 < len(parts):
                    flag_b64 = parts[i + 1]
                    # Clean it
                    flag_b64 = ''.join(c for c in flag_b64 if c.isalnum() or c in '+/=')
                    try:
                        decoded = base64.b64decode(flag_b64).decode('utf-8')
                        print(f"\n[+] DECODED FLAG: {decoded}")
                    except:
                        print(f"    Failed to decode: {flag_b64[:100]}")
    
    # Also look for base64-like patterns (long alphanumeric strings)
    base64_pattern = r'[A-Za-z0-9+/]{40,}={0,2}'
    matches = re.findall(base64_pattern, result)
    if matches:
        for match in matches[:5]:  # Try first 5
            try:
                decoded = base64.b64decode(match).decode('utf-8')
                if 'Kaal{' in decoded:
                    print(f"\n[+] Found base64 flag at bit {bit_pos}:")
                    print(f"    Base64: {match}")
                    print(f"    Decoded: {decoded}")
            except:
                pass

print("\n[*] Done")
