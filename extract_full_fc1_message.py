#!/usr/bin/env python3
"""
Extract the FULL message from fc1.weight including all hints
"""

import onnx
import struct
import re

model = onnx.load("challenge_final (1).onnx")

for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
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
        
        # Extract all readable sequences
        readable = re.findall(r'[ -~]{15,}', result[:20000])
        
        print("[*] All readable sequences from fc1.weight:")
        for i, seq in enumerate(readable[:20]):
            print(f"\n[{i}] {seq}")
        
        break
