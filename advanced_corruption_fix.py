#!/usr/bin/env python3
"""
Advanced corruption fixing - try to reconstruct the actual flag
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

# Find the corrupted flag
if 'Kaal{' in result:
    idx = result.index('Kaal{')
    flag_section = result[idx:idx+500]
    
    print("[*] Full corrupted section:")
    print(repr(flag_section[:300]))
    
    # We know:
    # Start: Kaal{l4yers_of_d3c03pt10n_m
    # End: @sk_7h3_pr353nc3_0f_pO1s0ns}
    
    # But wait - in Spider challenge, the middle was "m@sk"
    # Maybe here it's different?
    
    # Let me extract the bytes between start and end
    start_pattern = "Kaal{l4yers_of_d3c03pt10n_m"
    end_pattern = "@sk_7h3_pr353nc3_0f_pO1s0ns}"
    
    if end_pattern in flag_section:
        end_idx = flag_section.index(end_pattern)
        middle_bytes = flag_section[len(start_pattern):end_idx]
        
        print(f"\n[*] Middle section bytes:")
        print(f"  Length: {len(middle_bytes)} bytes")
        print(f"  Hex: {middle_bytes[:50].encode('latin-1').hex()}")
        print(f"  Repr: {repr(middle_bytes[:100])}")
        
        # Try to find patterns in the corruption
        # Look for ASCII characters
        ascii_chars = []
        for i, b in enumerate(middle_bytes):
            if 32 <= ord(b) < 127:
                ascii_chars.append((i, b))
        
        print(f"\n[*] ASCII characters in corruption:")
        for pos, char in ascii_chars[:30]:
            print(f"  Position {pos}: '{char}' (0x{ord(char):02x})")
        
        # Try to reconstruct by looking at bit patterns
        # Maybe only certain bits are corrupted?
        print(f"\n[*] Trying to fix corruption by testing different bit patterns...")
        
        # Get the float indices for this section
        start_byte_idx = idx + len(start_pattern)
        end_byte_idx = idx + end_idx
        
        # Convert byte indices to bit indices
        start_bit_idx = start_byte_idx * 8
        end_bit_idx = end_byte_idx * 8
        
        # Try extracting from different bit positions for this section
        for bit_pos in range(1, 8):
            section_bits = []
            for i in range(start_bit_idx, end_bit_idx):
                if i < len(bits):
                    float_idx = i // 8
                    if float_idx < len(floats):
                        int_repr = struct.unpack('I', struct.pack('f', floats[float_idx]))[0]
                        section_bits.append((int_repr >> bit_pos) & 1)
            
            if len(section_bits) >= 8:
                extracted_section = []
                for i in range(0, len(section_bits), 8):
                    if i + 8 <= len(section_bits):
                        byte_val = sum(section_bits[i+j] << j for j in range(8))
                        extracted_section.append(byte_val)
                
                result_section = bytes(extracted_section).decode('latin-1', errors='ignore')
                
                # Check if this looks more readable
                printable_count = sum(1 for c in result_section if 32 <= ord(c) < 127)
                if printable_count > len(result_section) * 0.7:
                    print(f"\n  [Bit {bit_pos}] More readable section:")
                    print(f"    {repr(result_section[:50])}")
                    
                    # Try to construct full flag
                    test_flag = f"Kaal{{l4yers_of_d3c03pt10n_m{result_section}{end_pattern}"
                    if len(result_section) < 30:
                        print(f"    Test flag: {test_flag}")

print("\n[*] Done")
