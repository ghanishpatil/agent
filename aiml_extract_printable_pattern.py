#!/usr/bin/env python3
"""
Look at the printable characters from the "first printable" strategy
and see if there's a pattern
"""

# From the output, the "first printable" gave us:
raw = b'Kaal{l4yers_of_d3c03pt10n_m0$13"fcA5=`4jE\xe0A!. *`uKa\'cO,-tYpV&C\\P;\xb9(KeR#9,$6(^-#W+6XhbF?jw6\'O-(@\x00Qxp,uJK1f1HCQd\xf7*kt+Uo(`8d{\\&2c3!u*\xf0Hu @N0F d I-+\\(\xb7eK"d00p<Pt0q$tl \\>*L5oJ4,V^<Vh\\V_%b^A|G-&2"ZzK?x\xd28QG~UgI^8u-gclg&ZTKWBH@@rB\\Ht`W.|6 (!+n(Ke+4zDAkv)ZJoc:@tt~@sk_7h3_pr353nc3_0f_pO1s0ns}'

# Extract only printable ASCII
printable = ''.join([chr(b) if 32 <= b < 127 else '' for b in raw])
print(f"[*] Printable characters only:")
print(printable)

# Look for the pattern - we know it starts with "l4yers_of_d3c03pt10n_m"
# and ends with "sk_7h3_pr353nc3_0f_pO1s0ns"

# The middle part from printable: "0$13"fcA5=`4jEA!. *`uKa'cO,-tYpV&C\P;(KeR#9,$6(^-#W+6XhbF?jw6'O-(@Qxp,uJK1f1HCQd*kt+Uo(`8d{\&2c3!u*Hu @N0F d I-+\(eK"d00p<Pt0q$tl \>*L5oJ4,V^<Vh\V_%b^A|G-&2"ZzK?x8QG~UgI^8u-gclg&ZTKWBH@@rB\Ht`W.|6 (!+n(Ke+4zDAkv)ZJoc:@tt~@"

# Let me try a different approach - maybe only certain positions are valid
# Let's look at the structure more carefully

import onnx
import struct

model = onnx.load(r"D:\mission-git-hackss\challenge_final (3).onnx")

fc1_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
        break

raw_data = fc1_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

# The hint says "sparse signals" - maybe we need to look at where weights are sparse
print("\n[*] Analyzing sparse weight positions...")

# Find sparse weights
sparse_threshold = 1e-6
sparse_indices = [i for i, f in enumerate(floats) if abs(f) < sparse_threshold]
print(f"[*] Found {len(sparse_indices)} sparse weights")

# Extract LSB from sparse positions only
bits_from_sparse = []
for idx in sparse_indices:
    int_repr = struct.unpack('I', struct.pack('f', floats[idx]))[0]
    bits_from_sparse.append(int_repr & 1)

if len(bits_from_sparse) >= 64:
    extracted = []
    for i in range(0, len(bits_from_sparse), 8):
        if i + 8 <= len(bits_from_sparse):
            byte_val = sum(bits_from_sparse[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"\n[*] From sparse positions:")
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        end = result.find('}', idx)
        if end != -1:
            flag = result[idx:end+1]
            print(f"  {flag}")

# Try another approach - maybe the "chord" means we need to look at 
# positions where MULTIPLE conditions are met
print("\n[*] Looking for positions where multiple conditions align...")

# Condition 1: Weight is sparse
# Condition 2: LSB is 1
# Condition 3: Specific bit pattern

aligned_positions = []
for i, f in enumerate(floats):
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    
    # Check multiple conditions
    is_sparse = abs(f) < sparse_threshold
    lsb_is_1 = (int_repr & 1) == 1
    
    # If both conditions met, this is part of the "chord"
    if is_sparse and lsb_is_1:
        aligned_positions.append(i)

print(f"[*] Found {len(aligned_positions)} aligned positions (sparse AND LSB=1)")

if len(aligned_positions) >= 64:
    bits = []
    for idx in aligned_positions:
        int_repr = struct.unpack('I', struct.pack('f', floats[idx]))[0]
        # Extract bit 1 instead of bit 0
        bits.append((int_repr >> 1) & 1)
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"\n[*] From aligned positions (bit 1):")
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        end = result.find('}', idx)
        if end != -1:
            flag = result[idx:end+1]
            printable_count = sum(1 for c in flag if c.isprintable())
            if printable_count / len(flag) > 0.9:
                print(f"  [+] CLEAN FLAG: {flag}")

print("\n[*] Done")
