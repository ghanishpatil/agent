#!/usr/bin/env python3
"""
The flag in fc1 is corrupted: Kaal{l4yers_of_d3c03pt10n_m<garbage>@sk_7h3_pr353nc3_0f_pO1s0ns}
Maybe the missing part is in other tensors at specific positions
"""

import onnx
import struct
import re

model = onnx.load("challenge_final (1).onnx")

# First, get the corrupted flag from fc1
fc1_data = None
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        raw_data = tensor.raw_data
        num_floats = len(raw_data) // 4
        floats = struct.unpack(f'{num_floats}f', raw_data)
        
        bits = []
        for f in floats:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            bits.append(int_repr & 1)
        
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
                extracted.append(byte_val)
        
        fc1_data = bytes(extracted).decode('latin-1', errors='ignore')
        break

# Find the flag
if 'Kaal{' in fc1_data:
    idx = fc1_data.index('Kaal{')
    # Get 300 chars after Kaal{
    flag_section = fc1_data[idx:idx+300]
    print("[*] Flag section from fc1:")
    print(repr(flag_section))
    
    # The pattern seems to be: Kaal{l4yers_of_d3c03pt10n_m<garbage>@sk_7h3_pr353nc3_0f_pO1s0ns}
    # Let's extract just the readable parts
    
    # Find where garbage starts
    match = re.search(r'Kaal\{([a-zA-Z0-9_]+)([^a-zA-Z0-9_]+)([a-zA-Z0-9_@]+)\}', flag_section)
    if match:
        part1, garbage, part2 = match.groups()
        print(f"\n[*] Part 1: {part1}")
        print(f"[*] Garbage: {repr(garbage[:50])}")
        print(f"[*] Part 2: {part2}")
        
        # The garbage might encode the position/length of missing part
        garbage_bytes = garbage.encode('latin-1')
        print(f"\n[*] Garbage bytes (hex): {garbage_bytes[:20].hex()}")
        print(f"[*] Garbage bytes (decimal): {[b for b in garbage_bytes[:20]]}")
        
        # Maybe the missing part is at a specific position in another tensor?
        # Let's check if any bytes in garbage look like indices
        
        # Try to find the missing part by looking at all tensors
        print("\n[*] Searching for middle part in other tensors...")
        
        for idx, tensor in enumerate(model.graph.initializer):
            if tensor.name == "fc1.weight":
                continue
                
            if not tensor.HasField('raw_data'):
                continue
            
            raw_data = tensor.raw_data
            num_floats = len(raw_data) // 4
            floats = struct.unpack(f'{num_floats}f', raw_data)
            
            bits = []
            for f in floats:
                int_repr = struct.unpack('I', struct.pack('f', f))[0]
                bits.append(int_repr & 1)
            
            extracted = []
            for i in range(0, len(bits), 8):
                if i + 8 <= len(bits):
                    byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
                    extracted.append(byte_val)
            
            result = bytes(extracted).decode('latin-1', errors='ignore')
            
            # Look for sequences that might fit between part1 and part2
            # Should connect "l4yers_of_d3c03pt10n_m" with "@sk_7h3_pr353nc3_0f_pO1s0ns"
            # Likely something like "ask" or "mask" or similar
            
            readable = re.findall(r'[a-zA-Z0-9_]{3,20}', result[:5000])
            for seq in readable:
                # Check if it could be the missing part
                if len(seq) >= 3 and len(seq) <= 10:
                    test_flag = f"Kaal{{{part1}{seq}{part2}}}"
                    # Check if it makes sense
                    if 'mask' in seq.lower() or 'ask' in seq.lower():
                        print(f"  [Tensor {idx}] Potential: {seq} -> {test_flag}")
