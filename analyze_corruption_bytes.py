#!/usr/bin/env python3
"""
Analyze the corruption byte by byte to find patterns
"""

import onnx
import struct

model = onnx.load("challenge_final 2.onnx")

# Get fc1.weight
fc1_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
        break

raw_data = fc1_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

# Extract LSB
bits = []
for f in floats:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    bits.append(int_repr & 1)

extracted = []
for i in range(0, len(bits), 8):
    if i + 8 <= len(bits):
        byte_val = sum(bits[i+j] << j for j in range(8))
        extracted.append(byte_val)

result = bytes(extracted).decode('latin-1', errors='ignore')

# Find the flag
if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+300]
    
    # We know the structure:
    # Kaal{l4yers_of_d3c03pt10n_m<CORRUPTION>@sk_7h3_pr353nc3_0f_pO1s0ns}
    
    start = "Kaal{l4yers_of_d3c03pt10n_m"
    end = "@sk_7h3_pr353nc3_0f_pO1s0ns}"
    
    if end in flag_section:
        end_idx = flag_section.index(end)
        corruption = flag_section[len(start):end_idx]
        
        print(f"[*] Corruption analysis:")
        print(f"  Length: {len(corruption)} bytes")
        print(f"  Hex: {corruption.encode('latin-1').hex()}")
        
        # Check if there's a pattern - maybe every Nth byte is correct?
        print(f"\n[*] Looking for patterns...")
        
        # Try extracting every 2nd byte
        every_2nd = corruption[::2]
        print(f"  Every 2nd byte: {repr(every_2nd)}")
        
        # Try extracting every 3rd byte
        every_3rd = corruption[::3]
        print(f"  Every 3rd byte: {repr(every_3rd)}")
        
        # Try extracting only printable ASCII
        printable = ''.join(c for c in corruption if 32 <= ord(c) < 127)
        print(f"  Printable only: {printable}")
        
        # Maybe the answer is just "m@sk" like in Spider challenge?
        print(f"\n[*] Testing if flag is same as Spider challenge:")
        test_flag = f"Kaal{{l4yers_of_d3c03pt10n_m@sk_7h3_pr353nc3_0f_pO1s0ns}}"
        print(f"  {test_flag}")
        
        # Or maybe it's a variation?
        variations = [
            "yst3ry_",
            "yst1c_",
            "yst1qu3_",
            "yst3r13s_",
            "yst1f1c4t10n_",
        ]
        
        print(f"\n[*] Testing variations:")
        for var in variations:
            test = f"Kaal{{l4yers_of_d3c03pt10n_m{var}{end}"
            print(f"  {test}")

print("\n[*] Done")
