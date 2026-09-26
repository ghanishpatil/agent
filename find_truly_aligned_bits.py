#!/usr/bin/env python3
"""
"sparse signals align and chord is triggered"
"signals in alignment will wake it"

What if "alignment" means positions where MULTIPLE tensors have LSB=1?
A chord = multiple bits set at the same position across different tensors
"""

import onnx
import struct

model = onnx.load("challenge_final (2).onnx")

# Get fc1, fc2, and head tensors
tensors_data = {}
for tensor in model.graph.initializer:
    if tensor.name in ['fc1.weight', 'fc2.weight', 'head.weight']:
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        floats = struct.unpack(f'{num_floats}f', raw)
        tensors_data[tensor.name] = floats
        print(f"[*] {tensor.name}: {len(floats)} floats")

fc1 = tensors_data['fc1.weight']
fc2 = tensors_data['fc2.weight']
head = tensors_data['head.weight']

# Extract LSB from each
def get_lsb_bits(floats):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append(int_repr & 1)
    return bits

fc1_bits = get_lsb_bits(fc1)
fc2_bits = get_lsb_bits(fc2)
head_bits = get_lsb_bits(head)

print(f"\n[*] Extracted LSB bits from all tensors")

# Find positions where ALL THREE have LSB=1 (chord/alignment)
# Since tensors are different sizes, we need to map positions
# Strategy: Use modulo to map fc2 and head positions to fc1

print(f"\n[*] Looking for aligned positions (all LSBs = 1)...")

aligned_positions = []
for i in range(len(fc1_bits)):
    fc2_idx = i % len(fc2_bits)
    head_idx = i % len(head_bits)
    
    if fc1_bits[i] == 1 and fc2_bits[fc2_idx] == 1 and head_bits[head_idx] == 1:
        aligned_positions.append(i)

print(f"[*] Found {len(aligned_positions)} aligned positions where all LSBs = 1")

if len(aligned_positions) > 0:
    print(f"[*] First 50 aligned positions: {aligned_positions[:50]}")
    
    # Now extract the BYTES at these aligned positions from fc1
    # Each aligned position gives us one BIT
    bits = [fc1_bits[pos] for pos in aligned_positions]
    
    # Convert to bytes
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    print(f"\n[*] Extracted {len(extracted)} bytes from aligned positions")
    
    # Look for flag
    if 'Kaal{' in result:
        start = result.index('Kaal{')
        end = result.find('}', start)
        if end != -1:
            flag = result[start:end+1]
            print(f"\n[+] FLAG FOUND: {flag}")
    else:
        print(f"\n[*] No Kaal{{ found")
        print(f"[*] First 500 chars:")
        print(result[:500])
        
        # Show readable fragments
        current = ""
        for c in result:
            if 32 <= ord(c) < 127:
                current += c
            else:
                if len(current) >= 15:
                    print(f"  Fragment: {current}")
                current = ""
else:
    print(f"[-] No aligned positions found")

print("\n[*] Done")
