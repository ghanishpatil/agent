#!/usr/bin/env python3
"""
Final Whisper - Maybe the answer is in reconstructing using all available data
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

# Extract the corrupted flag
if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+500]
    
    print("[*] Corrupted flag:")
    print(repr(flag_section[:300]))
    
    # We know the pattern from Spider challenge:
    # Kaal{l4yers_of_d3c03pt10n_m@sk_7h3_pr353nc3_0f_pO1s0ns}
    
    # But maybe for Final Whisper, the flag is different?
    # Let me look for the ending more carefully
    
    if '@sk_7h3_pr353nc3_0f_pO1s0ns}' in flag_section:
        end_part = '@sk_7h3_pr353nc3_0f_pO1s0ns}'
        end_idx = flag_section.index(end_part)
        
        print(f"\n[*] Found end part at position {end_idx}")
        print(f"  Before end: {repr(flag_section[:end_idx])}")
        
        # The beginning is: Kaal{l4yers_of_d3c03pt10n_m
        # The end is: @sk_7h3_pr353nc3_0f_pO1s0ns}
        
        # Maybe the middle part is different for this challenge?
        # Let me check if there's a pattern in the corruption
        
        middle_section = flag_section[27:end_idx]
        print(f"\n[*] Middle section ({len(middle_section)} bytes):")
        print(repr(middle_section))
        
        # Try to find any readable ASCII in the middle
        readable = ""
        for c in middle_section:
            if 32 <= ord(c) < 127:
                readable += c
            else:
                if readable:
                    print(f"  Readable fragment: {readable}")
                    readable = ""
        
        # Maybe the flag for Final Whisper is actually about the "whisper" itself
        # Let me try common words that fit the theme
        possible_middles = [
            "yst3ry_",  # mystery
            "yst3r13s_",  # mysteries
            "yst1c_",  # mystic
            "yst1f1c4t10n_",  # mystification
            "yst1qu3_",  # mystique
        ]
        
        for middle in possible_middles:
            test_flag = f"Kaal{{l4yers_of_d3c03pt10n_m{middle}{end_part}"
            print(f"\n  Testing: {test_flag}")

# Also check if there's any other HDWGT marker
print("\n[*] Checking for additional markers...")
for marker in ['HDWGT2', 'HDWGT3', 'WHISPER', 'FINAL', 'CHORD']:
    if marker in result:
        idx_m = result.index(marker)
        print(f"\n  Found {marker}:")
        section = result[idx_m:idx_m+300]
        print(f"  {repr(section)}")
        
        # Try to decode if it's base64
        if '|' in section:
            parts = section.split('|')
            for part in parts:
                if len(part) > 20 and part.replace('=', '').replace('+', '').replace('/', '').isalnum():
                    try:
                        decoded = base64.b64decode(part).decode()
                        print(f"    Decoded: {decoded}")
                    except:
                        pass

print("\n[*] Done")
