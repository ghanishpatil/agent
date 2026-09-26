#!/usr/bin/env python3
"""
Reconstruct the flag by analyzing ALL 4 markers
Maybe markers 2 and 3 contain clues to fix the corruption in markers 0 and 1
"""

import onnx
import struct

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

# Extract each marker section
markers = {
    0: result[512+8:768],
    1: result[768+8:1024],
    2: result[1024+8:1280],
    3: result[1280+8:1536]
}

print("[*] Analyzing marker sections:\n")

# Marker 0: Start of flag
marker0_str = markers[0].decode('latin-1', errors='ignore')
print(f"Marker 0: {marker0_str[:100]}")

# Marker 1: End of flag
marker1_str = markers[1].decode('latin-1', errors='ignore')
print(f"Marker 1: {marker1_str[:100]}")

# Find where the corruption starts in marker 0
flag_start = marker0_str.find('Kaal{l4yers_of_d3c03pt10n_m')
if flag_start >= 0:
    # Extract up to the corruption
    clean_part = 'Kaal{l4yers_of_d3c03pt10n_m'
    corruption_start = flag_start + len(clean_part)
    
    print(f"\n[*] Flag starts at offset {flag_start}")
    print(f"[*] Clean part: {clean_part}")
    print(f"[*] Corruption starts at byte {corruption_start}")
    
    # Look at the corrupted bytes
    corrupted_section = markers[0][corruption_start:corruption_start+20]
    print(f"[*] Corrupted bytes (hex): {corrupted_section.hex()}")
    print(f"[*] Corrupted bytes (dec): {[b for b in corrupted_section]}")

# Find where marker 1 starts
marker1_clean = marker1_str.find('@sk_7h3_pr353nc3_0f_pO1s0ns}')
if marker1_clean >= 0:
    print(f"\n[*] Marker 1 clean part starts at offset {marker1_clean}")
    print(f"[*] Clean ending: @sk_7h3_pr353nc3_0f_pO1s0ns}}")

# The missing part should connect "m" to "@sk"
# In the Spider challenge, we determined it was "m@sk"
# But what if there's MORE to it?

# Let me check if markers 2 or 3 contain hints
print(f"\n[*] Checking markers 2 and 3 for hints...")

for marker_num in [2, 3]:
    marker_str = markers[marker_num].decode('latin-1', errors='ignore')
    
    # Look for any readable text that might be the missing piece
    readable = ''
    for c in marker_str:
        if 32 <= ord(c) < 127:
            readable += c
        else:
            if len(readable) > 3:
                # Check if this could be the missing piece
                if any(x in readable.lower() for x in ['mask', 'ask', 'msk']):
                    print(f"  Marker {marker_num}: Found '{readable}'")
            readable = ''

# Try to reconstruct the flag
# The pattern is: Kaal{l4yers_of_d3c03pt10n_m???@sk_7h3_pr353nc3_0f_pO1s0ns}
# We know from Spider it's "m@sk" but let me verify

print(f"\n[*] Attempting reconstruction...")

# What if the missing part is NOT just "@" but something else?
# Let me look at the EXACT bytes between 'm' and '@sk'

# In marker 0, find 'm'
m_pos = marker0_str.find('Kaal{l4yers_of_d3c03pt10n_m')
if m_pos >= 0:
    m_pos += len('Kaal{l4yers_of_d3c03pt10n_m')
    
    # In marker 1, find '@sk'
    ask_pos = marker1_str.find('@sk_7h3_pr353nc3_0f_pO1s0ns}')
    
    if ask_pos >= 0:
        # The bytes between should tell us what's missing
        between_bytes_0 = markers[0][m_pos:m_pos+10]
        before_bytes_1 = markers[1][max(0, ask_pos-10):ask_pos]
        
        print(f"\n[*] Bytes after 'm' in marker 0: {between_bytes_0.hex()}")
        print(f"[*] Bytes before '@sk' in marker 1: {before_bytes_1.hex()}")
        
        # Try different interpretations
        # Maybe the corruption is actually part of the flag?
        # Or maybe I need to look at a different bit position?

# Let me try extracting from bit position 1 instead of 0
print(f"\n[*] Trying bit position 1...")

bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append((int_repr >> 1) & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result_bit1 = bytes(extracted)
marker0_bit1 = result_bit1[512+8:768].decode('latin-1', errors='ignore')

if 'Kaal{' in marker0_bit1:
    print(f"[+] Found flag in bit 1: {marker0_bit1[:100]}")

print("\n[*] Done")
