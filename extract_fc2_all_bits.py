#!/usr/bin/env python3
"""
Extract from fc2.weight using different bit positions
"only the right few signals in alignment"
"""

import onnx
import struct
import re

model = onnx.load("challenge_final (1).onnx")

for tensor in model.graph.initializer:
    if tensor.name == "fc2.weight":
        print(f"[*] Extracting from fc2.weight")
        
        raw_data = tensor.raw_data
        num_floats = len(raw_data) // 4
        floats = struct.unpack(f'{num_floats}f', raw_data)
        
        # Try different bit positions (0=LSB, 1=second bit, etc.)
        for bit_pos in range(8):
            print(f"\n[*] Trying bit position {bit_pos}")
            
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
            
            # Look for Kaal{ or HDWGT or FRAG
            if 'Kaal{' in result or 'HDWGT' in result or 'FRAG' in result:
                print(f"  [!] Found marker at bit position {bit_pos}!")
                print(f"  First 500 chars: {result[:500]}")
                
                if 'Kaal{' in result:
                    idx = result.index('Kaal{')
                    end = result.find('}', idx)
                    if end != -1:
                        flag = result[idx:end+1]
                        print(f"\n  [!] FLAG: {flag}")
                        break
            
            # Show first 100 chars for each bit position
            readable = re.findall(r'[ -~]{20,}', result[:1000])
            if readable:
                print(f"  Readable sequences: {len(readable)}")
                for seq in readable[:2]:
                    print(f"    {seq[:80]}")
        
        break
