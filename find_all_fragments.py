#!/usr/bin/env python3
"""
Find ALL fragments across all tensors
Look for FRAG0, FRAG1, FRAG2, etc. or PART0, PART1, etc.
"""

import onnx
import struct
import re
import base64

model = onnx.load("challenge_final (1).onnx")

all_fragments = {}

for idx, tensor in enumerate(model.graph.initializer):
    if not tensor.HasField('raw_data'):
        continue
    
    raw_data = tensor.raw_data
    num_floats = len(raw_data) // 4
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    # Extract LSB
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append(int_repr & 1)
    
    # Convert to bytes
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    # Look for fragment patterns
    # FRAG0|data, FRAG1|data, etc.
    frag_patterns = [
        r'FRAG(\d+)\|([^|]+)',
        r'PART(\d+)\|([^|]+)',
        r'PIECE(\d+)\|([^|]+)',
        r'F(\d+)\|([^|]+)',
        r'P(\d+)\|([^|]+)',
    ]
    
    for pattern in frag_patterns:
        matches = re.findall(pattern, result)
        if matches:
            print(f"\n[*] Tensor {idx} ({tensor.name}): Found {len(matches)} fragments")
            for num, data in matches:
                print(f"    Fragment {num}: {data[:80]}")
                all_fragments[int(num)] = data
    
    # Also look for HDWGT2, HDWGT3, etc. (different from HDWGT1 in first challenge)
    hdwgt_matches = re.findall(r'HDWGT(\d+)\|([^|]+)', result)
    if hdwgt_matches:
        print(f"\n[*] Tensor {idx} ({tensor.name}): Found HDWGT markers")
        for num, data in hdwgt_matches:
            print(f"    HDWGT{num}: {data[:100]}")

# Assemble fragments
if all_fragments:
    print("\n" + "="*60)
    print("[*] Assembling fragments in order:")
    print("="*60)
    
    sorted_frags = sorted(all_fragments.items())
    for num, data in sorted_frags:
        print(f"\nFragment {num}:")
        print(f"  {data[:200]}")
    
    # Try to assemble
    full_data = ''.join(data for _, data in sorted_frags)
    print(f"\n[*] Assembled data ({len(full_data)} chars):")
    print(full_data[:500])
    
    # Try base64 decode
    try:
        decoded = base64.b64decode(full_data).decode('utf-8')
        print(f"\n[!] Base64 decoded:")
        print(decoded)
    except:
        print("\n[-] Not base64 encoded")
    
    # Look for Kaal{ in assembled
    if 'Kaal{' in full_data:
        idx = full_data.index('Kaal{')
        end = full_data.find('}', idx)
        if end != -1:
            flag = full_data[idx:end+1]
            print(f"\n[!] FLAG FOUND: {flag}")
else:
    print("\n[-] No fragments found with standard markers")
    print("[*] Trying alternative approach - looking for sequential readable strings...")
