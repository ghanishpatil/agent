#!/usr/bin/env python3
"""
FINAL ATTEMPT: Extract byte N from ALL tensors, then byte N+1 from all tensors, etc.
Each tensor contributes one character at each position
"""
import onnx, struct

model = onnx.load("challenge_final (1).onnx")

# Extract LSB from all tensors
tensor_data = []
for tensor in model.graph.initializer:
    if not tensor.HasField('raw_data'):
        tensor_data.append([])
        continue
    
    floats = struct.unpack(f'{len(tensor.raw_data)//4}f', tensor.raw_data)
    bits = [(struct.unpack('I', struct.pack('f', f))[0] & 1) for f in floats]
    extracted = [sum(bits[i+j] << j for j in range(8)) for i in range(0, len(bits), 8) if i+8 <= len(bits)]
    tensor_data.append(extracted)

print(f"[*] Extracted from {len(tensor_data)} tensors")

# Method: For each byte position, collect one byte from each tensor
flag_bytes = []
for pos in range(200):  # Try first 200 positions
    for t_idx, data in enumerate(tensor_data):
        if pos < len(data):
            flag_bytes.append(data[pos])

result = bytes(flag_bytes).decode('latin-1', errors='ignore')
print(f"[*] Result (first 500): {result[:500]}")

if 'Kaal{' in result:
    idx = result.index('Kaal{')
    end = result.find('}', idx)
    if end != -1:
        flag = result[idx:end+1]
        print(f"\n[!] FLAG: {flag}")
    else:
        print(f"\n[*] Kaal{{ found at {idx}: {result[idx:idx+200]}")
