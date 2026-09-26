#!/usr/bin/env python3
"""
Extract readable strings from each tensor
Maybe each tensor index IS the fragment number
"""

import onnx
import struct
import re
import base64

model = onnx.load("challenge_final (1).onnx")

tensor_data = {}

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
    
    # Extract all readable ASCII sequences
    readable = re.findall(r'[ -~]{10,}', result[:2000])
    
    if readable:
        print(f"\n[Tensor {idx}] {tensor.name}:")
        for seq in readable[:5]:
            print(f"  {seq[:100]}")
        
        tensor_data[idx] = {
            'name': tensor.name,
            'readable': readable,
            'full': result[:2000]
        }

# Try to find flag pieces
print("\n" + "="*60)
print("[*] Looking for flag-like patterns in each tensor")
print("="*60)

flag_pieces = {}

for idx, data in tensor_data.items():
    for seq in data['readable']:
        # Look for Kaal{ or parts that look like flag content
        if 'Kaal' in seq or re.search(r'[a-zA-Z0-9_]{20,}', seq):
            print(f"\n[Tensor {idx}] Potential flag content:")
            print(f"  {seq[:150]}")
            
            # Try to extract just alphanumeric parts
            clean = re.findall(r'[a-zA-Z0-9_{}]+', seq)
            if clean:
                flag_pieces[idx] = ''.join(clean)

# Try assembling by tensor order
if flag_pieces:
    print("\n[*] Assembling by tensor index order:")
    sorted_pieces = sorted(flag_pieces.items())
    for idx, piece in sorted_pieces:
        print(f"  [{idx}]: {piece[:100]}")
    
    assembled = ''.join(piece for _, piece in sorted_pieces)
    print(f"\n[*] Assembled: {assembled[:300]}")
    
    if 'Kaal{' in assembled:
        start = assembled.index('Kaal{')
        end = assembled.find('}', start)
        if end != -1:
            flag = assembled[start:end+1]
            print(f"\n[!] FLAG: {flag}")
