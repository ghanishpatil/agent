#!/usr/bin/env python3
"""
Compare the three ONNX models
"""

import onnx
import struct
import hashlib

models = [
    ("challenge_final.onnx", "Varys Part 1"),
    ("challenge_final (1).onnx", "Spider Part 2"),
    ("challenge_final 2.onnx", "Final Whisper")
]

for filename, name in models:
    try:
        model = onnx.load(filename)
        
        # Get fc1.weight
        fc1_tensor = None
        for tensor in model.graph.initializer:
            if tensor.name == "fc1.weight":
                fc1_tensor = tensor
                break
        
        if fc1_tensor:
            raw_data = fc1_tensor.raw_data
            data_hash = hashlib.md5(raw_data).hexdigest()
            print(f"\n[{name}]")
            print(f"  File: {filename}")
            print(f"  fc1.weight size: {len(raw_data)} bytes")
            print(f"  MD5: {data_hash}")
            
            # Extract first 500 bytes of LSB
            num_floats = min(4000, len(raw_data) // 4)
            floats = struct.unpack(f'{num_floats}f', raw_data[:num_floats*4])
            
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
            if 'Kaal{' in result:
                idx = result.index('Kaal{')
                print(f"  Flag preview: {result[idx:idx+100]}")
    except Exception as e:
        print(f"\n[{name}] Error: {e}")

print("\n[*] Done")
