#!/usr/bin/env python3
"""
New interpretation: "the last whisper waits at fc2; only the right few signals"
- The whisper data is in fc1 (as before)
- fc2 tells us WHICH positions to extract ("only the right few signals")
- Use fc2 values as selectors/indices
"""

import onnx
import struct
import numpy as np

model = onnx.load("challenge_final (2).onnx")

# Get fc1 and fc2
fc1_data = None
fc2_data = None

for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        fc1_data = struct.unpack(f'{num_floats}f', raw)
    elif tensor.name == "fc2.weight":
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        fc2_data = struct.unpack(f'{num_floats}f', raw)

print(f"[*] fc1.weight: {len(fc1_data)} floats")
print(f"[*] fc2.weight: {len(fc2_data)} floats")

# Strategy 1: Use fc2 values as indices into fc1
# Take the integer part of fc2 values as positions
print("\n[*] Strategy 1: fc2 values as indices")
indices = []
for val in fc2_data:
    idx = int(abs(val) * 1000) % len(fc1_data)  # Scale and modulo
    indices.append(idx)

# Extract LSB from fc1 at these positions
bits = []
for idx in indices:
    int_repr = struct.unpack('I', struct.pack('f', fc1_data[idx]))[0]
    bits.append(int_repr & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

if 'Kaal{' in result:
    start = result.index('Kaal{')
    end = result.find('}', start)
    if end != -1:
        print(f"[+] FLAG FOUND (Strategy 1): {result[start:end+1]}")
else:
    print(f"[-] No flag in Strategy 1")
    print(f"    First 200 chars: {result[:200]}")

# Strategy 2: Use positions where fc2 has specific pattern
# "only the right few signals" - maybe where fc2 > threshold
print("\n[*] Strategy 2: fc2 values above threshold")
threshold = 0.5
selected_positions = [i for i, val in enumerate(fc2_data) if abs(val) > threshold]
print(f"[*] Found {len(selected_positions)} positions with |fc2| > {threshold}")

if len(selected_positions) > 0:
    # Map to fc1 positions (fc2 is smaller, so use modulo)
    bits = []
    for pos in selected_positions:
        fc1_pos = pos % len(fc1_data)
        int_repr = struct.unpack('I', struct.pack('f', fc1_data[fc1_pos]))[0]
        bits.append(int_repr & 1)
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    if 'Kaal{' in result:
        start = result.index('Kaal{')
        end = result.find('}', start)
        if end != -1:
            print(f"[+] FLAG FOUND (Strategy 2): {result[start:end+1]}")
    else:
        print(f"[-] No flag in Strategy 2")

# Strategy 3: Use top N values from fc2
print("\n[*] Strategy 3: Top 2048 fc2 values")
fc2_array = np.array(fc2_data)
top_indices = np.argsort(np.abs(fc2_array))[-2048:]  # Top 2048 by magnitude

bits = []
for idx in top_indices:
    fc1_pos = idx % len(fc1_data)
    int_repr = struct.unpack('I', struct.pack('f', fc1_data[fc1_pos]))[0]
    bits.append(int_repr & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

if 'Kaal{' in result:
    start = result.index('Kaal{')
    end = result.find('}', start)
    if end != -1:
        print(f"[+] FLAG FOUND (Strategy 3): {result[start:end+1]}")
else:
    print(f"[-] No flag in Strategy 3")

print("\n[*] Done")
