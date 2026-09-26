#!/usr/bin/env python3
"""
Search for ALL HDWGT structures in the file
Maybe there's a third one I missed
"""

import onnx
import struct
import base64
import re

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

result = bytes(extracted)

print("[*] Searching for HDWGT structures...\n")

# Find all HDWGT occurrences
offset = 0
count = 0
while True:
    idx = result.find(b'HDWGT', offset)
    if idx == -1:
        break
    
    count += 1
    print(f"[*] HDWGT #{count} at offset {idx}")
    
    # Extract 500 bytes
    section = result[idx:idx+500]
    
    # Try to parse structure
    section_str = section.decode('latin-1', errors='ignore')
    
    if '|FLAG|' in section_str:
        parts = section_str.split('|')
        print(f"    Structure parts: {[p[:20] + '...' if len(p) > 20 else p for p in parts[:6]]}")
        
        # Try to decode FLAG
        for i, part in enumerate(parts):
            if part == 'FLAG' and i + 1 < len(parts):
                flag_b64 = parts[i + 1]
                # Clean it
                flag_b64_clean = ''.join(c for c in flag_b64 if c.isalnum() or c in '+/=')
                if len(flag_b64_clean) > 20:
                    try:
                        decoded = base64.b64decode(flag_b64_clean).decode('utf-8')
                        print(f"    FLAG: {decoded}")
                    except:
                        print(f"    FLAG (failed to decode): {flag_b64_clean[:50]}")
            
            if part == 'HINT' and i + 1 < len(parts):
                hint_b64 = parts[i + 1]
                hint_b64_clean = ''.join(c for c in hint_b64 if c.isalnum() or c in '+/=')
                if len(hint_b64_clean) > 20:
                    try:
                        decoded = base64.b64decode(hint_b64_clean).decode('utf-8')
                        print(f"    HINT: {decoded}")
                    except:
                        print(f"    HINT (failed to decode): {hint_b64_clean[:50]}")
    
    print()
    offset = idx + 1

print(f"\n[*] Total HDWGT structures found: {count}")

# Also search for any other base64-like long strings
print(f"\n[*] Searching for other base64 patterns...")
base64_pattern = rb'[A-Za-z0-9+/]{60,}={0,2}'
matches = re.findall(base64_pattern, result)

print(f"[*] Found {len(matches)} base64-like patterns")

for i, match in enumerate(matches[:10]):
    try:
        decoded = base64.b64decode(match).decode('utf-8')
        if 'Kaal{' in decoded:
            print(f"\n[+] Pattern {i+1} contains flag:")
            print(f"    Base64: {match[:80]}")
            print(f"    Decoded: {decoded}")
    except:
        pass

print("\n[*] Done")
