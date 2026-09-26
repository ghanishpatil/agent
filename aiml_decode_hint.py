#!/usr/bin/env python3
"""
Analyze the HDWGT marker more carefully
The hint says "up next, the little birds carry only"
This might mean we need to look at what comes AFTER the hint
"""

import onnx
import struct
import base64

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

# Extract LSB from bit 0
bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append(int_repr & 1)

# Convert to string
extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

# Find the HDWGT marker
if 'HDWGT' in result:
    idx = result.index('HDWGT')
    print(f"[*] Found HDWGT at index {idx}")
    
    # Get a large context
    context = result[idx:idx+1000]
    print(f"\n[*] Full context around HDWGT:")
    print(context)
    
    # Decode the hint
    if '|HINT|' in context:
        hint_start = context.index('|HINT|') + 6
        hint_end = context.find('|', hint_start)
        if hint_end == -1:
            hint_end = len(context)
        
        hint_b64 = context[hint_start:hint_end]
        print(f"\n[*] Hint (base64): {hint_b64}")
        
        try:
            hint_decoded = base64.b64decode(hint_b64).decode('utf-8')
            print(f"[*] Hint (decoded): {hint_decoded}")
        except:
            print(f"[*] Could not decode hint")
    
    # Look for what comes after
    print(f"\n[*] Looking for data after the hint...")
    
    # Find where the hint section ends
    if '|HINT|' in context:
        hint_section_end = context.rfind('|')
        after_hint = context[hint_section_end+1:]
        print(f"\n[*] Data after hint section:")
        print(f"    Length: {len(after_hint)} chars")
        print(f"    First 500 chars: {after_hint[:500]}")
        
        # Check if there's another Kaal{ flag
        if 'Kaal{' in after_hint:
            flag_start = after_hint.index('Kaal{')
            flag_end = after_hint.find('}', flag_start)
            if flag_end != -1:
                potential_flag = after_hint[flag_start:flag_end+1]
                print(f"\n[+] Found another Kaal{{ after hint: {potential_flag}")

# Now try other bit positions - "little birds" might mean sparse/small bits
print("\n" + "="*60)
print("[*] Trying other bit positions (little birds = small bits?)")
print("="*60)

for bit_pos in range(1, 8):
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
    
    # Look for clean Kaal{ flags (not the decoy)
    if 'Kaal{' in result:
        # Find all occurrences
        start_idx = 0
        while True:
            idx = result.find('Kaal{', start_idx)
            if idx == -1:
                break
            
            end_idx = result.find('}', idx)
            if end_idx != -1 and end_idx - idx < 200:
                flag = result[idx:end_idx+1]
                
                # Check if it's mostly printable and not the decoy
                printable = sum(1 for c in flag if 32 <= ord(c) < 127)
                if printable / len(flag) > 0.9 and '1f_TiMe' not in flag:
                    print(f"\n[+] Bit {bit_pos}: Found flag: {flag}")
            
            start_idx = idx + 1

print("\n[*] Done")
