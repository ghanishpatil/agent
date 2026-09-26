#!/usr/bin/env python3
"""
Comprehensive search for the flag in the ONNX model
Try all possible interpretations of "chord" and "sparse signals"
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

def bits_to_string(bits):
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    return bytes(extracted).decode('latin-1', errors='ignore')

def check_for_flag(result, strategy_name):
    if 'Kaal{' in result:
        start = result.index('Kaal{')
        end = result.find('}', start)
        if end != -1 and end - start < 200:
            flag = result[start:end+1]
            # Check if it's mostly printable
            printable = sum(1 for c in flag if 32 <= ord(c) < 127)
            if printable / len(flag) > 0.9:
                print(f"\n{'='*60}")
                print(f"[+] FOUND FLAG with {strategy_name}!")
                print(f"[+] {flag}")
                print(f"{'='*60}\n")
                return True
    return False

# Get main tensors
fc1 = tensors.get('fc1.weight', [])
fc2 = tensors.get('fc2.weight', [])
head = tensors.get('head.weight', [])

print(f"[*] fc1: {len(fc1)} floats")
print(f"[*] fc2: {len(fc2)} floats")
print(f"[*] head: {len(head)} floats")

# Strategy 1: Multi-bit chord - extract where multiple bits are set
print("\n[*] Strategy 1: Multi-bit chord (multiple bits set simultaneously)")
for tensor_name, floats in [('fc1.weight', fc1), ('fc2.weight', fc2), ('head.weight', head)]:
    if not floats:
        continue
    
    # Find positions where bits 0,1,2 form specific patterns
    for pattern in [(1,1,1), (0,0,0), (1,0,1), (0,1,0)]:
        bits = []
        for f in floats:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            b0 = (int_repr >> 0) & 1
            b1 = (int_repr >> 1) & 1
            b2 = (int_repr >> 2) & 1
            
            if (b0, b1, b2) == pattern:
                # Extract bit 3 as data
                bits.append((int_repr >> 3) & 1)
        
        if len(bits) >= 64:
            result = bits_to_string(bits)
            if check_for_flag(result, f"{tensor_name} pattern {pattern}"):
                exit(0)

# Strategy 2: Sparse weight positions
print("\n[*] Strategy 2: Using sparse weight positions")
for tensor_name, floats in [('fc1.weight', fc1), ('fc2.weight', fc2)]:
    if not floats:
        continue
    
    # Find very small weights (sparse)
    sparse_indices = [i for i, f in enumerate(floats) if abs(f) < 1e-6]
    print(f"  {tensor_name}: {len(sparse_indices)} sparse weights")
    
    # Extract from sparse positions
    for bit_pos in range(8):
        bits = []
        for idx in sparse_indices:
            int_repr = struct.unpack('I', struct.pack('f', floats[idx]))[0]
            bits.append((int_repr >> bit_pos) & 1)
        
        if len(bits) >= 64:
            result = bits_to_string(bits)
            if check_for_flag(result, f"{tensor_name} sparse bit {bit_pos}"):
                exit(0)

# Strategy 3: Use fc2 as selector for fc1
print("\n[*] Strategy 3: FC2 selects positions from FC1")
if fc1 and fc2:
    for bit_pos in range(8):
        # Get fc2 LSB as selector
        fc2_selector = []
        for f in fc2:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            fc2_selector.append(int_repr & 1)
        
        # Use selector to pick from fc1
        bits = []
        for i, f in enumerate(fc1):
            selector_idx = i % len(fc2_selector)
            if fc2_selector[selector_idx] == 1:
                int_repr = struct.unpack('I', struct.pack('f', f))[0]
                bits.append((int_repr >> bit_pos) & 1)
        
        if len(bits) >= 64:
            result = bits_to_string(bits)
            if check_for_flag(result, f"FC2 selects FC1 bit {bit_pos}"):
                exit(0)

# Strategy 4: Use head as selector for fc1
print("\n[*] Strategy 4: Head selects positions from FC1")
if fc1 and head:
    for bit_pos in range(8):
        # Get head LSB as selector
        head_selector = []
        for f in head:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            head_selector.append(int_repr & 1)
        
        # Use selector to pick from fc1
        bits = []
        for i, f in enumerate(fc1):
            selector_idx = i % len(head_selector)
            if head_selector[selector_idx] == 1:
                int_repr = struct.unpack('I', struct.pack('f', f))[0]
                bits.append((int_repr >> bit_pos) & 1)
        
        if len(bits) >= 64:
            result = bits_to_string(bits)
            if check_for_flag(result, f"Head selects FC1 bit {bit_pos}"):
                exit(0)

# Strategy 5: XOR combination (chord = combination)
print("\n[*] Strategy 5: XOR combination of tensors")
if fc1 and fc2:
    for bit_pos in range(8):
        bits = []
        for i in range(min(len(fc1), len(fc2))):
            int1 = struct.unpack('I', struct.pack('f', fc1[i]))[0]
            int2 = struct.unpack('I', struct.pack('f', fc2[i % len(fc2)]))[0]
            
            b1 = (int1 >> bit_pos) & 1
            b2 = (int2 >> bit_pos) & 1
            bits.append(b1 ^ b2)
        
        if len(bits) >= 64:
            result = bits_to_string(bits)
            if check_for_flag(result, f"FC1 XOR FC2 bit {bit_pos}"):
                exit(0)

# Strategy 6: Look in other tensors
print("\n[*] Strategy 6: Checking all other tensors")
for tensor_name, floats in tensors.items():
    if tensor_name in ['fc1.weight', 'fc2.weight', 'head.weight']:
        continue
    
    for bit_pos in range(8):
        bits = []
        for f in floats:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            bits.append((int_repr >> bit_pos) & 1)
        
        if len(bits) >= 64:
            result = bits_to_string(bits)
            if check_for_flag(result, f"{tensor_name} bit {bit_pos}"):
                exit(0)

print("\n[*] No flag found in any strategy")
