#!/usr/bin/env python3
"""
Extract clean flag from fc1.weight tensor
"""

import onnx
import struct
import re

def extract_flag_from_fc1():
    model = onnx.load("challenge_final.onnx")
    
    # Find fc1.weight tensor
    for tensor in model.graph.initializer:
        if tensor.name == "fc1.weight" and tensor.HasField('raw_data'):
            raw_data = tensor.raw_data
            print(f"[*] Found fc1.weight: {len(raw_data)} bytes")
            
            # Parse as float32 values
            num_floats = len(raw_data) // 4
            floats = struct.unpack(f'{num_floats}f', raw_data)
            
            print(f"[*] Number of floats: {num_floats}")
            
            # Extract LSB from integer representation of floats
            bits = []
            for f in floats:
                int_repr = struct.unpack('I', struct.pack('f', f))[0]
                bits.append(int_repr & 1)
            
            # Convert bits to bytes
            extracted = []
            for i in range(0, len(bits), 8):
                if i + 8 <= len(bits):
                    byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
                    extracted.append(byte_val)
            
            result = bytes(extracted).decode('latin-1', errors='ignore')
            
            # Find all occurrences of Kaal{...}
            flags = re.findall(r'Kaal\{[^}]+\}', result)
            
            print(f"\n[*] Found {len(flags)} potential flags:")
            for i, flag in enumerate(flags):
                print(f"\n[{i+1}] {flag}")
                # Check if it's printable ASCII
                if all(32 <= ord(c) < 127 or c in '\n\r\t' for c in flag):
                    print(f"    -> This looks clean!")
            
            # Also try to extract just the flag part manually
            if 'Kaal{' in result:
                start = result.index('Kaal{')
                # Find the closing brace, but only look for printable chars
                end_search = result[start:]
                clean_flag = "Kaal{"
                i = 5  # Start after "Kaal{"
                while i < len(end_search):
                    c = end_search[i]
                    if c == '}':
                        clean_flag += '}'
                        break
                    elif 32 <= ord(c) < 127:  # Printable ASCII
                        clean_flag += c
                    i += 1
                
                print(f"\n[*] Manually extracted clean flag:")
                print(f"    {clean_flag}")
                
                return clean_flag
    
    return None

if __name__ == "__main__":
    flag = extract_flag_from_fc1()
    
    if flag:
        print("\n" + "="*60)
        print(f"FINAL FLAG: {flag}")
        print("="*60)
