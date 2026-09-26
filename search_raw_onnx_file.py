#!/usr/bin/env python3
"""
Search the RAW ONNX file bytes for Kaal{ flags
Maybe there's data outside the tensors
"""

import re

# Read raw file
with open("challenge_final (2).onnx", 'rb') as f:
    raw_data = f.read()

print(f"[*] File size: {len(raw_data)} bytes")
print(f"[*] Searching for 'Kaal{{' in raw bytes...\n")

# Search for Kaal{
pattern = rb'Kaal\{[^\}]{10,150}\}'
matches = re.findall(pattern, raw_data)

print(f"[*] Found {len(matches)} potential flags\n")

for i, match in enumerate(matches):
    try:
        flag_str = match.decode('utf-8')
        # Check if clean
        if all(32 <= ord(c) < 127 for c in flag_str):
            print(f"  {i+1}. {flag_str}")
            
            # Check if it's a known flag
            if '1f_TiMe_c4n_b3_cr34tEd' in flag_str:
                print(f"      (Varys Part 1)")
            elif 'l4yers_of_d3c03pt10n' in flag_str:
                print(f"      (Spider Part 2 - corrupted)")
            else:
                print(f"      [NEW FLAG!]")
    except:
        pass

print("\n[*] Done")
