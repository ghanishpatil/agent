#!/usr/bin/env python3
"""
Search ALL tensors for Kaal{ flags
Maybe the Final Whisper flag is in a different tensor
"""

import onnx
import struct
import re

model = onnx.load("challenge_final (2).onnx")

print("[*] Searching all tensors for flags...\n")

for tensor in model.graph.initializer:
    raw_data = tensor.raw_data
    if len(raw_data) == 0:
        continue
    
    num_floats = len(raw_data) // 4
    if num_floats == 0:
        continue
    
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    # Try all bit positions
    for bit_pos in range(32):
        bits = []
        for f in floats:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            bits.append((int_repr >> bit_pos) & 1)
        
        # Convert to bytes
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_val = sum(bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        
        # Look for Kaal{
        if 'Kaal{' in result:
            # Find all matches
            for match in re.finditer(r'Kaal\{[^\}]{0,200}\}', result):
                flag = match.group()
                # Check if it's a clean flag (no garbage bytes)
                clean = True
                for c in flag:
                    if ord(c) < 32 or ord(c) > 126:
                        clean = False
                        break
                
                if clean:
                    print(f"[+] CLEAN FLAG FOUND!")
                    print(f"    Tensor: {tensor.name}")
                    print(f"    Bit position: {bit_pos}")
                    print(f"    Flag: {flag}")
                    print()

print("\n[*] Search complete")
