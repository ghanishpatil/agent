#!/usr/bin/env python3
"""
Extract the flag by filtering out garbage bytes
The flag parts are: "l4yers_of_d3c03pt10n_m" + ??? + "sk_7h3_pr353nc3_0f_pO1s0ns"
"""

import onnx
import struct

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

# Extract from bit 0
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

# Find the Kaal{ that's not the decoy
idx = 0
while True:
    idx = result.find(b'Kaal{', idx)
    if idx == -1:
        break
    
    # Check if it's the decoy
    if b'1f_TiMe' in result[idx:idx+100]:
        idx += 1
        continue
    
    # Found the real flag location
    print(f"[*] Found real flag at byte index {idx}")
    
    # Extract a large chunk
    chunk = result[idx:idx+500]
    
    # Find where it ends
    end_idx = chunk.find(b'}')
    if end_idx != -1:
        flag_bytes = chunk[:end_idx+1]
        print(f"\n[*] Raw flag bytes ({len(flag_bytes)} bytes):")
        print(f"    {flag_bytes}")
        
        # Try to clean it - keep only printable ASCII
        cleaned = []
        in_flag = False
        for b in flag_bytes:
            if b == ord('K') or (in_flag and b == ord('{')):
                in_flag = True
                cleaned.append(b)
            elif in_flag:
                # Keep printable ASCII characters
                if 32 <= b < 127:
                    cleaned.append(b)
                elif b == ord('}'):
                    cleaned.append(b)
                    break
        
        cleaned_str = bytes(cleaned).decode('latin-1', errors='ignore')
        print(f"\n[*] Cleaned (printable only): {cleaned_str}")
        
        # Try another approach - the middle part might be in a different bit position
        # Let's extract the positions of the clean parts
        start_part = b'l4yers_of_d3c03pt10n_m'
        end_part = b'sk_7h3_pr353nc3_0f_pO1s0ns'
        
        start_pos = flag_bytes.find(start_part)
        end_pos = flag_bytes.find(end_part)
        
        if start_pos != -1 and end_pos != -1:
            print(f"\n[*] Start part at: {start_pos}")
            print(f"[*] End part at: {end_pos}")
            print(f"[*] Gap size: {end_pos - (start_pos + len(start_part))} bytes")
            
            # The gap might contain the missing part
            gap = flag_bytes[start_pos + len(start_part):end_pos]
            print(f"\n[*] Gap bytes: {gap}")
            print(f"[*] Gap (hex): {gap.hex()}")
            
            # Try to extract printable characters from gap
            gap_printable = bytes([b for b in gap if 32 <= b < 127])
            print(f"[*] Gap printable: {gap_printable}")
    
    break

# Now try extracting from multiple bit positions and combining
print("\n" + "="*60)
print("[*] Trying multi-bit extraction (chord approach)")
print("="*60)

# The hint says "little birds carry only fragments"
# Maybe each bit position carries a different part of the flag

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
    
    result_bytes = bytes(extracted)
    
    # Look for the middle part - something between 'm' and 'sk'
    # Common CTF patterns: m4sk, mask, m@sk, etc.
    for pattern in [b'm4sk_', b'mask_', b'm@sk_', b'm$sk_', b'm4$k_', b'ma5k_']:
        if pattern in result_bytes:
            idx = result_bytes.find(pattern)
            context = result_bytes[max(0, idx-30):idx+50]
            print(f"\n[Bit {bit_pos}] Found '{pattern.decode()}' at {idx}:")
            print(f"  Context: {context}")

print("\n[*] Done")
