#!/usr/bin/env python3
"""
Extract ALL WGT1 structures from the file
"""

import base64
import re

with open("challenge_final (2).onnx", 'rb') as f:
    raw_data = f.read()

print("[*] Searching for all WGT1 structures...\n")

# Find all WGT1 occurrences
offset = 0
count = 0
while True:
    idx = raw_data.find(b'WGT1|FLAG|', offset)
    if idx == -1:
        break
    
    count += 1
    # Extract 300 bytes
    section = raw_data[idx:idx+300]
    section_str = section.decode('latin-1', errors='ignore')
    
    print(f"{'='*80}")
    print(f"WGT1 Structure #{count} at offset 0x{idx:x}")
    print(f"{'='*80}")
    
    # Parse structure
    if '|' in section_str:
        # Find the end (next WGT or newline)
        end_idx = section_str.find('WGT', 10)
        if end_idx == -1:
            end_idx = section_str.find('\n', 10)
        if end_idx == -1:
            end_idx = 250
        
        structure = section_str[:end_idx]
        parts = structure.split('|')
        
        # Extract FLAG
        for i, part in enumerate(parts):
            if part == 'FLAG' and i + 1 < len(parts):
                flag_b64 = parts[i + 1]
                flag_clean = ''.join(c for c in flag_b64 if c.isalnum() or c in '+/=')
                try:
                    flag_decoded = base64.b64decode(flag_clean).decode('utf-8')
                    print(f"FLAG: {flag_decoded}")
                except:
                    print(f"FLAG (decode failed): {flag_clean[:60]}")
        
        # Extract HINT
        for i, part in enumerate(parts):
            if part == 'HINT' and i + 1 < len(parts):
                hint_b64 = parts[i + 1]
                hint_clean = ''.join(c for c in hint_b64 if c.isalnum() or c in '+/=')
                try:
                    hint_decoded = base64.b64decode(hint_clean).decode('utf-8')
                    print(f"HINT: {hint_decoded}")
                except:
                    print(f"HINT (decode failed): {hint_clean[:60]}")
    
    print()
    offset = idx + 1

print(f"\n[*] Total WGT1 structures found: {count}")
print("\n[*] Done")
