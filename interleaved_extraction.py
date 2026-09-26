#!/usr/bin/env python3
"""
Extract interleaved bytes - byte 0 from tensor 0, byte 1 from tensor 1, etc.
"each whisper remembers its place"
"""

import onnx
import struct

model = onnx.load("challenge_final (1).onnx")

# Extract LSB from all tensors
all_tensor_data = []

for idx, tensor in enumerate(model.graph.initializer):
    if not tensor.HasField('raw_data'):
        all_tensor_data.append([])
        continue
    
    raw_data = tensor.raw_data
    num_floats = len(raw_data) // 4
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append(int_repr & 1)
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
            extracted.append(byte_val)
    
    all_tensor_data.append(extracted)

print(f"[*] Extracted data from {len(all_tensor_data)} tensors")

# Try interleaved extraction - round-robin through tensors
print("\n[*] Trying interleaved extraction (round-robin)...")

max_len = max(len(data) for data in all_tensor_data if data)
flag_bytes = []

for byte_idx in range(min(1000, max_len)):
    for tensor_idx, data in enumerate(all_tensor_data):
        if byte_idx < len(data):
            flag_bytes.append(data[byte_idx])

result = bytes(flag_bytes).decode('latin-1', errors='ignore')
print(f"First 500 chars: {result[:500]}")

if 'Kaal{' in result:
    idx = result.index('Kaal{')
    end = result.find('}', idx)
    if end != -1:
        flag = result[idx:end+1]
        print(f"\n[!] FLAG FOUND: {flag}")
