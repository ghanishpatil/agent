#!/usr/bin/env python3
"""
Try running the ONNX model with different inputs
"tiny, coordinated set of inputs played together" suggests specific input patterns
"""

import onnx
import onnxruntime as ort
import numpy as np

model_path = r"D:\mission-git-hackss\challenge_final (3).onnx"

# Load model
model = onnx.load(model_path)

# Check input shape
input_info = model.graph.input[0]
print(f"[*] Input name: {input_info.name}")
print(f"[*] Input type: {input_info.type}")

# Get input shape
input_shape = []
for dim in input_info.type.tensor_type.shape.dim:
    if dim.dim_value:
        input_shape.append(dim.dim_value)
    else:
        input_shape.append(1)  # Default for dynamic dims

print(f"[*] Input shape: {input_shape}")

# Check outputs
print(f"\n[*] Outputs:")
for output in model.graph.output:
    print(f"  - {output.name}")

# Create session
session = ort.InferenceSession(model_path)

# Try different input patterns
print("\n[*] Testing different input patterns...")

# Pattern 1: All zeros
print("\n[1] All zeros:")
input_data = np.zeros(input_shape, dtype=np.float32)
outputs = session.run(None, {input_info.name: input_data})
for i, out in enumerate(outputs):
    print(f"  Output {i}: shape={out.shape}, sample={out.flatten()[:10]}")
    # Check if output contains flag
    out_bytes = out.tobytes()
    if b'Kaal{' in out_bytes:
        print(f"  [+] FOUND FLAG in output {i}!")
        idx = out_bytes.index(b'Kaal{')
        print(f"  {out_bytes[idx:idx+100]}")

# Pattern 2: All ones
print("\n[2] All ones:")
input_data = np.ones(input_shape, dtype=np.float32)
outputs = session.run(None, {input_info.name: input_data})
for i, out in enumerate(outputs):
    print(f"  Output {i}: shape={out.shape}, sample={out.flatten()[:10]}")
    out_bytes = out.tobytes()
    if b'Kaal{' in out_bytes:
        print(f"  [+] FOUND FLAG in output {i}!")
        idx = out_bytes.index(b'Kaal{')
        print(f"  {out_bytes[idx:idx+100]}")

# Pattern 3: Specific "chord" pattern - small coordinated values
print("\n[3] Chord pattern (specific small values):")
# Try a pattern where only specific positions are set
input_data = np.zeros(input_shape, dtype=np.float32)
# Set specific positions to 1 (like playing specific notes in a chord)
if len(input_shape) == 4:  # Batch, Channel, Height, Width
    # Set a few specific pixels
    input_data[0, 0, 0, 0] = 1.0
    input_data[0, 0, 0, 1] = 1.0
    input_data[0, 0, 1, 0] = 1.0
elif len(input_shape) == 2:  # Batch, Features
    input_data[0, 0] = 1.0
    input_data[0, 1] = 1.0
    input_data[0, 2] = 1.0

outputs = session.run(None, {input_info.name: input_data})
for i, out in enumerate(outputs):
    print(f"  Output {i}: shape={out.shape}, sample={out.flatten()[:10]}")
    out_bytes = out.tobytes()
    if b'Kaal{' in out_bytes:
        print(f"  [+] FOUND FLAG in output {i}!")
        idx = out_bytes.index(b'Kaal{')
        print(f"  {out_bytes[idx:idx+100]}")

# Pattern 4: Random small values
print("\n[4] Random sparse pattern:")
input_data = np.random.rand(*input_shape).astype(np.float32) * 0.1
outputs = session.run(None, {input_info.name: input_data})
for i, out in enumerate(outputs):
    print(f"  Output {i}: shape={out.shape}, sample={out.flatten()[:10]}")
    out_bytes = out.tobytes()
    if b'Kaal{' in out_bytes:
        print(f"  [+] FOUND FLAG in output {i}!")
        idx = out_bytes.index(b'Kaal{')
        print(f"  {out_bytes[idx:idx+100]}")

# Pattern 5: Try extracting from output LSBs
print("\n[5] Extracting LSB from outputs:")
input_data = np.zeros(input_shape, dtype=np.float32)
outputs = session.run(None, {input_info.name: input_data})

import struct

for out_idx, out in enumerate(outputs):
    flat = out.flatten()
    bits = []
    for val in flat:
        int_repr = struct.unpack('I', struct.pack('f', val))[0]
        bits.append(int_repr & 1)
    
    if len(bits) >= 64:
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_val = sum(bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        if 'Kaal{' in result:
            print(f"\n  [+] FOUND FLAG in output {out_idx} LSB!")
            start = result.index('Kaal{')
            end = result.find('}', start)
            if end != -1:
                print(f"  {result[start:end+1]}")

print("\n[*] Done")
