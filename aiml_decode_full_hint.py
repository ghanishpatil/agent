#!/usr/bin/env python3
"""
Decode the full hint properly - it got cut off before
"""

import base64

# The hint base64 from the HDWGT marker (before it got corrupted)
# Let me extract it more carefully

import onnx
import struct

model = onnx.load(r"D:\mission-git-hackss\challenge_final (3).onnx")

fc1_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
        break

raw_data = fc1_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

# Extract LSB from bit 0
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

# Find HDWGT
idx = result.find(b'HDWGT')
if idx != -1:
    # Extract the section
    section = result[idx:idx+500]
    print(f"[*] HDWGT section (raw bytes):")
    print(section[:300])
    
    # Find the HINT marker
    hint_start = section.find(b'|HINT|')
    if hint_start != -1:
        hint_start += 6
        # Find the next pipe or non-base64 character
        hint_data = section[hint_start:]
        
        # Base64 characters are A-Z, a-z, 0-9, +, /, =
        hint_b64 = b''
        for b in hint_data:
            if (65 <= b <= 90) or (97 <= b <= 122) or (48 <= b <= 57) or b in [43, 47, 61]:
                hint_b64 += bytes([b])
            else:
                break
        
        print(f"\n[*] Hint base64: {hint_b64}")
        print(f"[*] Length: {len(hint_b64)}")
        
        try:
            hint_decoded = base64.b64decode(hint_b64).decode('utf-8')
            print(f"\n[*] Hint decoded:")
            print(f"    {hint_decoded}")
        except Exception as e:
            print(f"\n[-] Could not decode: {e}")
            
            # Try with padding
            for padding in ['', '=', '==', '===']:
                try:
                    hint_decoded = base64.b64decode(hint_b64 + padding.encode()).decode('utf-8')
                    print(f"\n[*] Hint decoded (with {len(padding)} padding):")
                    print(f"    {hint_decoded}")
                    break
                except:
                    continue

print("\n[*] Done")
