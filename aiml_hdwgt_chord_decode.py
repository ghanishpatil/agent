#!/usr/bin/env python3
"""
Look for HDWGT markers and use them to decode the chord
HDWGT might indicate "hidden weight" positions that form the chord
"""

import onnx
import struct

model = onnx.load(r"D:\mission-git-hackss\challenge_final (3).onnx")

# Extract all tensors
tensors = {}
for tensor in model.graph.initializer:
    if tensor.HasField('raw_data'):
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        floats = struct.unpack(f'{num_floats}f', raw)
        tensors[tensor.name] = floats

def get_bits(floats, bit_pos=0):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append((int_repr >> bit_pos) & 1)
    return bits

def bits_to_string(bits):
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    return bytes(extracted).decode('latin-1', errors='ignore')

print("[*] Searching for HDWGT markers...")

# Find all HDWGT markers in all tensors
hdwgt_info = []

for tensor_name, floats in tensors.items():
    for bit_pos in range(8):
        bits = get_bits(floats, bit_pos)
        result = bits_to_string(bits)
        
        if 'HDWGT' in result:
            idx = result.index('HDWGT')
            # Get context around HDWGT
            context = result[max(0, idx-50):idx+200]
            hdwgt_info.append({
                'tensor': tensor_name,
                'bit_pos': bit_pos,
                'index': idx,
                'context': context
            })
            print(f"\n[+] Found HDWGT in {tensor_name}, bit {bit_pos} at index {idx}")
            print(f"    Context: {context[:150]}")

if not hdwgt_info:
    print("[-] No HDWGT markers found")
else:
    print(f"\n[*] Found {len(hdwgt_info)} HDWGT markers")
    
    # Now try to decode using the HDWGT information
    print("\n[*] Attempting to decode using HDWGT markers...")
    
    for info in hdwgt_info:
        tensor_name = info['tensor']
        bit_pos = info['bit_pos']
        context = info['context']
        
        # Look for instructions after HDWGT
        if 'Kaal{' in context:
            print(f"\n[+] FOUND FLAG in {tensor_name} bit {bit_pos}!")
            start = context.index('Kaal{')
            end = context.find('}', start)
            if end != -1:
                flag = context[start:end+1]
                print(f"[+] FLAG: {flag}")
        
        # Look for patterns like "bit:X" or "pos:Y" that might indicate how to decode
        if ':' in context:
            print(f"\n[*] Found colon in context for {tensor_name} bit {bit_pos}")
            print(f"    {context}")

# Try combining multiple tensors at HDWGT positions
if len(hdwgt_info) >= 2:
    print("\n[*] Trying to combine multiple HDWGT-marked tensors (chord)...")
    
    # Get the tensors that have HDWGT
    hdwgt_tensors = list(set([info['tensor'] for info in hdwgt_info]))
    print(f"[*] Tensors with HDWGT: {hdwgt_tensors}")
    
    if len(hdwgt_tensors) >= 2:
        # Try XOR combination
        t1_name = hdwgt_tensors[0]
        t2_name = hdwgt_tensors[1]
        
        t1_floats = tensors[t1_name]
        t2_floats = tensors[t2_name]
        
        for bit_pos in range(8):
            t1_bits = get_bits(t1_floats, bit_pos)
            t2_bits = get_bits(t2_floats, bit_pos)
            
            # XOR the bits
            min_len = min(len(t1_bits), len(t2_bits))
            xor_bits = [t1_bits[i] ^ t2_bits[i] for i in range(min_len)]
            
            result = bits_to_string(xor_bits)
            if 'Kaal{' in result:
                print(f"\n[+] FOUND FLAG with XOR of {t1_name} and {t2_name}, bit {bit_pos}!")
                start = result.index('Kaal{')
                end = result.find('}', start)
                if end != -1 and end - start < 200:
                    flag = result[start:end+1]
                    print(f"[+] FLAG: {flag}")

# Try looking at specific bit combinations (chord = multiple bits)
print("\n[*] Trying multi-bit chord extraction from HDWGT tensors...")

for info in hdwgt_info:
    tensor_name = info['tensor']
    floats = tensors[tensor_name]
    
    # Extract where bits 0,1,2 form specific patterns
    for pattern_name, pattern_func in [
        ("all_same", lambda b0,b1,b2: b0==b1==b2),
        ("majority_1", lambda b0,b1,b2: (b0+b1+b2)>=2),
        ("exactly_2", lambda b0,b1,b2: (b0+b1+b2)==2),
        ("xor_pattern", lambda b0,b1,b2: (b0^b1^b2)==1),
    ]:
        bits = []
        for f in floats:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            b0 = (int_repr >> 0) & 1
            b1 = (int_repr >> 1) & 1
            b2 = (int_repr >> 2) & 1
            
            if pattern_func(b0, b1, b2):
                # Extract bit 3 as data
                bits.append((int_repr >> 3) & 1)
        
        if len(bits) >= 64:
            result = bits_to_string(bits)
            if 'Kaal{' in result and 'HDWGT' not in result:
                print(f"\n[+] FOUND FLAG in {tensor_name} with pattern {pattern_name}!")
                start = result.index('Kaal{')
                end = result.find('}', start)
                if end != -1 and end - start < 200:
                    flag = result[start:end+1]
                    printable = sum(1 for c in flag if 32 <= ord(c) < 127)
                    if printable / len(flag) > 0.9:
                        print(f"[+] FLAG: {flag}")

print("\n[*] Done")
