#!/usr/bin/env python3
"""
Extract fragments from fc2.weight - "the last whisper waits at fc2"
"""

import onnx
import struct
import re
import base64

model = onnx.load("challenge_final (1).onnx")

print("[*] Looking for fc2.weight tensor...")

for tensor in model.graph.initializer:
    if tensor.name == "fc2.weight":
        print(f"[+] Found fc2.weight")
        print(f"    Size: {len(tensor.raw_data)} bytes")
        
        raw_data = tensor.raw_data
        num_floats = len(raw_data) // 4
        floats = struct.unpack(f'{num_floats}f', raw_data)
        
        print(f"    Number of floats: {num_floats}")
        
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
        
        result = bytes(extracted)
        result_str = result.decode('latin-1', errors='ignore')
        
        print(f"\n[*] First 2000 characters:")
        print(result_str[:2000])
        
        # Look for structured data
        print(f"\n[*] Looking for pipe-delimited data...")
        if '|' in result_str[:5000]:
            parts = result_str[:5000].split('|')
            for i, part in enumerate(parts[:30]):
                if part.strip() and len(part) > 3:
                    print(f"  Part {i}: {repr(part[:100])}")
        
        # Look for FRAG markers
        print(f"\n[*] Looking for fragment markers...")
        frag_matches = re.findall(r'(FRAG|PART|PIECE)(\d+)\|([^|]+)', result_str[:10000])
        for match in frag_matches:
            print(f"  {match[0]}{match[1]}: {match[2][:50]}")
        
        # Look for base64
        print(f"\n[*] Looking for base64 encoded data...")
        b64_matches = re.findall(r'[A-Za-z0-9+/]{30,}={0,2}', result_str[:10000])
        for i, b64 in enumerate(b64_matches[:10]):
            try:
                decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
                if len(decoded) > 5:
                    print(f"  Match {i}: {decoded[:100]}")
            except:
                pass
        
        # Look for Kaal{ patterns
        print(f"\n[*] Looking for Kaal{{ patterns...")
        if 'Kaal{' in result_str:
            idx = result_str.index('Kaal{')
            print(f"  Found at position {idx}")
            print(f"  Context: {repr(result_str[max(0,idx-50):idx+200])}")
        
        # Look for HDWGT markers like in fc1
        print(f"\n[*] Looking for HDWGT markers...")
        if 'HDWGT' in result_str:
            idx = result_str.index('HDWGT')
            print(f"  Found at position {idx}")
            print(f"  Context: {result_str[idx:idx+500]}")
        
        break
