#!/usr/bin/env python3
"""
Try different interpretations of "chord" and "alignment":
1. Positions where EXACTLY 2 tensors have LSB=1 (partial chord)
2. Positions where fc2 LSB=1 (fc2 selects which fc1 bits to use)
3. Positions where head LSB=1 (head selects which fc1 bits to use)
"""

import onnx
import struct

model = onnx.load("challenge_final (2).onnx")

# Get tensors
tensors_data = {}
for tensor in model.graph.initializer:
    if tensor.name in ['fc1.weight', 'fc2.weight', 'head.weight']:
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        floats = struct.unpack(f'{num_floats}f', raw)
        tensors_data[tensor.name] = floats

fc1 = tensors_data['fc1.weight']
fc2 = tensors_data['fc2.weight']
head = tensors_data['head.weight']

def get_lsb_bits(floats):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append(int_repr & 1)
    return bits

fc1_bits = get_lsb_bits(fc1)
fc2_bits = get_lsb_bits(fc2)
head_bits = get_lsb_bits(head)

def try_extraction(positions, name):
    """Extract bytes from fc1 at given positions"""
    if len(positions) == 0:
        print(f"[-] {name}: No positions found")
        return
    
    print(f"\n[*] {name}: {len(positions)} positions")
    
    # Get bits from fc1 at these positions
    bits = [fc1_bits[pos] for pos in positions]
    
    # Convert to bytes
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    
    # Look for flag
    if 'Kaal{' in result:
        start = result.index('Kaal{')
        end = result.find('}', start)
        if end != -1:
            print(f"[+] FLAG FOUND: {result[start:end+1]}")
            return True
    
    # Show sample
    readable = sum(1 for c in result if 32 <= ord(c) < 127)
    print(f"    Readable: {readable}/{len(result)} chars")
    if readable > 100:
        print(f"    Sample: {result[:200]}")
    
    return False

# Strategy 1: Positions where fc2 LSB=1 (fc2 selects from fc1)
print("[*] Strategy 1: Where fc2 LSB=1")
positions = [i for i in range(len(fc1_bits)) if fc2_bits[i % len(fc2_bits)] == 1]
if try_extraction(positions, "FC2 selects"):
    exit(0)

# Strategy 2: Positions where head LSB=1 (head selects from fc1)
print("\n[*] Strategy 2: Where head LSB=1")
positions = [i for i in range(len(fc1_bits)) if head_bits[i % len(head_bits)] == 1]
if try_extraction(positions, "Head selects"):
    exit(0)

# Strategy 3: Positions where EXACTLY 2 out of 3 have LSB=1
print("\n[*] Strategy 3: Where exactly 2/3 have LSB=1")
positions = []
for i in range(len(fc1_bits)):
    fc2_idx = i % len(fc2_bits)
    head_idx = i % len(head_bits)
    count = fc1_bits[i] + fc2_bits[fc2_idx] + head_bits[head_idx]
    if count == 2:
        positions.append(i)
if try_extraction(positions, "Exactly 2/3"):
    exit(0)

# Strategy 4: Positions where fc1 AND fc2 have LSB=1 (but not head)
print("\n[*] Strategy 4: Where fc1 AND fc2 have LSB=1")
positions = []
for i in range(len(fc1_bits)):
    fc2_idx = i % len(fc2_bits)
    if fc1_bits[i] == 1 and fc2_bits[fc2_idx] == 1:
        positions.append(i)
if try_extraction(positions, "FC1 AND FC2"):
    exit(0)

# Strategy 5: Positions where fc1 AND head have LSB=1
print("\n[*] Strategy 5: Where fc1 AND head have LSB=1")
positions = []
for i in range(len(fc1_bits)):
    head_idx = i % len(head_bits)
    if fc1_bits[i] == 1 and head_bits[head_idx] == 1:
        positions.append(i)
if try_extraction(positions, "FC1 AND Head"):
    exit(0)

print("\n[*] No flag found in any strategy")
