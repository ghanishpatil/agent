#!/usr/bin/env python3
"""
Final Whisper - Check ALL tensors for hidden data
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

print(f"[*] Model has {len(model.graph.initializer)} tensors\n")

for idx, tensor in enumerate(model.graph.initializer):
    if not tensor.HasField('raw_data'):
        continue
    
    print(f"[Tensor {idx}] {tensor.name}")
    print(f"  Size: {len(tensor.raw_data)} bytes, dims: {tensor.dims}")
    
    raw_data = tensor.raw_data
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
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    # Look for any interesting markers
    markers = ['Kaal{', 'HDWGT', 'CHORD', 'SPARSE', 'FINAL', 'WHISPER', 'FLAG']
    found_any = False
    for marker in markers:
        if marker in result:
            if not found_any:
                print(f"  Found markers:")
                found_any = True
            idx_m = result.index(marker)
            preview = result[idx_m:idx_m+100].replace('\n', ' ').replace('\r', '')
            print(f"    {marker}: {preview}")
    
    # Also check for base64-like patterns
    if 'S2Fhb' in result or 'S2FhbH' in result:
        print(f"  Found base64 pattern!")
        idx_m = result.index('S2Fhb')
        print(f"    {result[idx_m:idx_m+100]}")
    
    if not found_any:
        # Show first 100 chars if printable
        printable = ''.join(c if 32 <= ord(c) < 127 else '.' for c in result[:100])
        if printable.strip('.'):
            print(f"  Preview: {printable}")
    
    print()

print("[*] Done")
