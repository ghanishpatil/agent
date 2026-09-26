#!/usr/bin/env python3
"""
Dump all readable ASCII from fc1.weight LSB extraction
"""

import onnx
import struct
import re

model = onnx.load("challenge_final.onnx")

for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        raw_data = tensor.raw_data
        
        # Parse as float32
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
        
        result = bytes(extracted)
        
        # Find all Kaal{ patterns
        result_str = result.decode('latin-1', errors='ignore')
        
        print("[*] Searching for all 'Kaal{' occurrences...")
        
        idx = 0
        count = 0
        while True:
            idx = result_str.find('Kaal{', idx)
            if idx == -1:
                break
            
            count += 1
            # Extract 200 chars after Kaal{
            snippet = result_str[idx:idx+200]
            
            # Try to find the closing brace
            end = snippet.find('}')
            if end != -1:
                potential_flag = snippet[:end+1]
                # Check if it's mostly printable
                printable_count = sum(1 for c in potential_flag if 32 <= ord(c) < 127)
                ratio = printable_count / len(potential_flag)
                
                print(f"\n[{count}] Found at position {idx}")
                print(f"    Printable ratio: {ratio:.2f}")
                print(f"    Raw: {repr(snippet[:100])}")
                
                if ratio > 0.7:  # Mostly printable
                    print(f"    Looks good: {potential_flag}")
            
            idx += 1
        
        print(f"\n[*] Total 'Kaal{{' occurrences: {count}")
        
        # Also try to extract only printable ASCII sequences
        print("\n[*] Extracting long printable ASCII sequences...")
        printable_sequences = re.findall(r'[ -~]{20,}', result_str)
        
        for i, seq in enumerate(printable_sequences[:10]):
            if 'Kaal' in seq or 'flag' in seq.lower():
                print(f"\n[{i+1}] {seq}")
        
        break
