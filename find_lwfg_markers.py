#!/usr/bin/env python3
"""
Search for LWFG markers in all tensors
"""

import onnx
import struct
import base64

model = onnx.load("challenge_final (1).onnx")

lwfg_data = {}

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
    
    # Search for LWFG
    if 'LWFG' in result:
        print(f"\n[Tensor {idx}] {tensor.name}: Found LWFG")
        idx_start = result.index('LWFG')
        context = result[idx_start:idx_start+500]
        print(f"  Context: {context}")
        
        # Try to parse LWFG structure
        # Format might be: LWFG<num>|<data>
        import re
        match = re.search(r'LWFG(\d+)\|([^|]+)', context)
        if match:
            num, data = match.groups()
            print(f"  LWFG{num}: {data[:100]}")
            lwfg_data[int(num)] = data

# Assemble LWFG data
if lwfg_data:
    print("\n" + "="*60)
    print("[*] Assembling LWFG data:")
    print("="*60)
    
    sorted_data = sorted(lwfg_data.items())
    for num, data in sorted_data:
        print(f"\nLWFG{num}:")
        print(f"  {data[:200]}")
    
    # Try to assemble
    full = ''.join(data for _, data in sorted_data)
    print(f"\n[*] Assembled ({len(full)} chars):")
    print(full[:500])
    
    # Try base64 decode
    try:
        decoded = base64.b64decode(full).decode('utf-8')
        print(f"\n[!] Base64 decoded:")
        print(decoded)
        
        if 'Kaal{' in decoded:
            print(f"\n[!] FLAG FOUND: {decoded}")
    except Exception as e:
        print(f"\n[-] Not base64: {e}")
