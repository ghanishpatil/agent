#!/usr/bin/env python3
"""
The hint says "little birds carry only fragments; each whisper remembers its place"
This means we need to extract fragments from multiple bit positions and combine them
"""

import onnx
import struct
import re

model = onnx.load(r"D:\mission-git-hackss\challenge_final (3).onnx")

# Extract fc1.weight
fc1_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
        break

raw_data = fc1_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

print("[*] Extracting fragments from all bit positions...")

fragments = []

for bit_pos in range(8):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append((int_repr >> bit_pos) & 1)
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    # Find all Kaal{ patterns
    for match in re.finditer(r'Kaal\{[^}]*\}?', result):
        fragment = match.group()
        # Skip the decoy flag
        if '1f_TiMe' not in fragment:
            fragments.append({
                'bit_pos': bit_pos,
                'fragment': fragment,
                'index': match.start()
            })
            print(f"\n[Bit {bit_pos}] Found fragment at index {match.start()}:")
            print(f"  {fragment}")

print(f"\n[*] Found {len(fragments)} fragments total")

# Try to reconstruct the flag
print("\n" + "="*60)
print("[*] Attempting to reconstruct the flag...")
print("="*60)

# Look for patterns that might indicate order or position
# The hint says "each whisper remembers its place"

# Strategy 1: Sort by bit position
print("\n[Strategy 1] Ordered by bit position:")
for frag in sorted(fragments, key=lambda x: x['bit_pos']):
    print(f"  Bit {frag['bit_pos']}: {frag['fragment']}")

# Strategy 2: Try to find overlapping parts and merge
print("\n[Strategy 2] Looking for overlapping fragments...")

# Extract just the content between Kaal{ and }
flag_parts = []
for frag in fragments:
    content = frag['fragment']
    if content.startswith('Kaal{'):
        content = content[5:]  # Remove 'Kaal{'
    if content.endswith('}'):
        content = content[:-1]  # Remove '}'
    
    if content and len(content) > 3:  # Skip very short fragments
        flag_parts.append({
            'bit_pos': frag['bit_pos'],
            'content': content,
            'index': frag['index']
        })

print(f"\n[*] Extracted {len(flag_parts)} content parts:")
for part in flag_parts:
    print(f"  Bit {part['bit_pos']}: {part['content']}")

# Strategy 3: Try concatenating in different orders
print("\n[Strategy 3] Trying different concatenation orders...")

# Order by bit position
ordered_by_bit = sorted(flag_parts, key=lambda x: x['bit_pos'])
concat_by_bit = ''.join([p['content'] for p in ordered_by_bit])
print(f"\n  By bit position: Kaal{{{concat_by_bit}}}")

# Order by index in the extracted string
ordered_by_index = sorted(flag_parts, key=lambda x: x['index'])
concat_by_index = ''.join([p['content'] for p in ordered_by_index])
print(f"  By index: Kaal{{{concat_by_index}}}")

# Strategy 4: Look for natural breaks and piece together
print("\n[Strategy 4] Smart reconstruction...")

# Look at the fragments more carefully
for part in flag_parts:
    content = part['content']
    # Check if it starts with lowercase letter (likely continuation)
    # or ends with underscore (likely incomplete)
    starts_lower = content[0].islower() if content else False
    ends_underscore = content.endswith('_') if content else False
    
    print(f"  Bit {part['bit_pos']}: '{content}'")
    print(f"    Starts lower: {starts_lower}, Ends underscore: {ends_underscore}")

# Try manual reconstruction based on patterns
print("\n[Strategy 5] Manual pattern matching...")

# I see: "l4yers_of_d3c03pt10n_m" and "sk_7h3_pr353nc3_0f_pO1s0ns"
# These might connect: "l4yers_of_d3c03pt10n_m[ask]_7h3_pr353nc3_0f_pO1s0ns"

possible_flags = [
    "Kaal{l4yers_of_d3c03pt10n_mask_7h3_pr353nc3_0f_pO1s0ns}",
    "Kaal{l4yers_of_d3c03pt10n_m4sk_7h3_pr353nc3_0f_pO1s0ns}",
]

print("\n[*] Possible reconstructed flags:")
for flag in possible_flags:
    print(f"  {flag}")

print("\n[*] Done")
