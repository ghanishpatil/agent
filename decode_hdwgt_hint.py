#!/usr/bin/env python3
"""
Decode the HDWGT hint - maybe it tells us how to find the third flag
"""

import onnx
import struct
import base64

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

# Find HDWGT marker
if 'HDWGT1' in result:
    idx = result.index('HDWGT1')
    hdwgt_section = result[idx:idx+500]
    
    print("[*] HDWGT section:")
    print(hdwgt_section)
    
    # Parse the structure
    parts = hdwgt_section.split('|')
    print(f"\n[*] Parts: {len(parts)}")
    for i, part in enumerate(parts[:10]):
        print(f"  Part {i}: {part[:100]}")
    
    # Decode the hint
    if len(parts) >= 5:
        hint_b64 = parts[4]
        try:
            hint = base64.b64decode(hint_b64).decode()
            print(f"\n[*] Decoded HINT:")
            print(f"  {hint}")
            
            # The hint from challenge 1 was: "up next, the little birds carry only fragments; each whisper remembers its place"
            # Maybe there's a different hint for challenge 3?
        except Exception as e:
            print(f"  Error decoding hint: {e}")
    
    # Check if there are more HDWGT markers
    print(f"\n[*] Looking for additional HDWGT markers...")
    for marker_num in range(2, 10):
        marker = f"HDWGT{marker_num}"
        if marker in result:
            idx_m = result.index(marker)
            print(f"\n  Found {marker}!")
            section = result[idx_m:idx_m+500]
            print(f"  {section[:200]}")
            
            # Try to parse it
            parts_m = section.split('|')
            if len(parts_m) >= 3:
                for i, part in enumerate(parts_m[:6]):
                    if part and len(part) > 10 and part.replace('=', '').replace('+', '').replace('/', '').isalnum():
                        try:
                            decoded = base64.b64decode(part).decode()
                            print(f"    Part {i} decoded: {decoded}")
                        except:
                            pass

print("\n[*] Done")
