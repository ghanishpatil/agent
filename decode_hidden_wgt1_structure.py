#!/usr/bin/env python3
"""
Decode the WGT1 structure found after the troll flag
"""

import base64

# The base64 strings from the WGT1 structure
flag_b64 = "S2FhbHtzdXJmYWNlX2ZsYWdf c3RyaW5nX3NlYXJjaF93aWxsX25vdF9zb2x2ZV90aGlzfQ=="
hint_b64 = "dGhpcyBlbnZlbG9wZSBpcyBhIHZpc2"

# Clean them
flag_b64 = flag_b64.replace(" ", "")

print("[*] Decoding WGT1 FLAG...")
try:
    flag_decoded = base64.b64decode(flag_b64).decode('utf-8')
    print(f"FLAG: {flag_decoded}")
except Exception as e:
    print(f"Error: {e}")

print("\n[*] Decoding WGT1 HINT...")
try:
    hint_decoded = base64.b64decode(hint_b64).decode('utf-8')
    print(f"HINT: {hint_decoded}")
except Exception as e:
    print(f"Error: {e}")

# Let me extract the full hint from the raw file
print("\n[*] Extracting full HINT from raw file...")
with open("challenge_final (2).onnx", 'rb') as f:
    raw_data = f.read()

# Find WGT1|FLAG|...
wgt1_pos = raw_data.find(b'WGT1|FLAG|')
if wgt1_pos >= 0:
    # Extract next 500 bytes
    section = raw_data[wgt1_pos:wgt1_pos+500]
    section_str = section.decode('latin-1', errors='ignore')
    
    print(f"\n[*] Full WGT1 structure:")
    print(section_str[:400])
    
    # Parse it
    if '|HINT|' in section_str:
        parts = section_str.split('|')
        for i, part in enumerate(parts):
            if part == 'HINT' and i + 1 < len(parts):
                hint_b64_full = parts[i + 1]
                # Clean and decode
                hint_clean = ''.join(c for c in hint_b64_full if c.isalnum() or c in '+/=')
                if len(hint_clean) > 10:
                    try:
                        hint_decoded = base64.b64decode(hint_clean).decode('utf-8')
                        print(f"\n[+] FULL HINT: {hint_decoded}")
                    except:
                        print(f"\n[*] Hint base64 (couldn't decode): {hint_clean[:100]}")

print("\n[*] Done")
