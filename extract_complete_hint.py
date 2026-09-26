#!/usr/bin/env python3
"""
Extract the complete HDWGT hint properly
"""

import onnx
import struct
import base64
import re

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

# Find HDWGT marker and extract using regex
pattern = r'HDWGT1\|FLAG\|([A-Za-z0-9+/=]+)\|HINT\|([A-Za-z0-9+/=]+)'
match = re.search(pattern, result)

if match:
    flag_b64 = match.group(1)
    hint_b64 = match.group(2)
    
    print("[*] Found HDWGT1 marker")
    print(f"  FLAG (base64): {flag_b64}")
    print(f"  HINT (base64): {hint_b64}")
    
    try:
        flag = base64.b64decode(flag_b64).decode()
        print(f"\n[*] Decoded FLAG:")
        print(f"  {flag}")
    except Exception as e:
        print(f"  Error decoding flag: {e}")
    
    try:
        hint = base64.b64decode(hint_b64).decode()
        print(f"\n[*] Decoded HINT:")
        print(f"  {hint}")
    except Exception as e:
        print(f"  Error decoding hint: {e}")

# Also look for any other structured markers
print(f"\n[*] Looking for other markers...")
for marker in ['HDWGT2', 'HDWGT3', 'FINAL', 'CHORD', 'SPARSE', 'WHISPER', 'THIRD', 'LAST']:
    if marker in result:
        idx = result.index(marker)
        print(f"\n  Found {marker} at position {idx}")
        section = result[idx:idx+300]
        # Try to find base64 patterns
        b64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        matches = re.findall(b64_pattern, section)
        for m in matches[:3]:
            try:
                decoded = base64.b64decode(m).decode()
                if len(decoded) > 5:
                    print(f"    Decoded: {decoded}")
            except:
                pass

print("\n[*] Done")
