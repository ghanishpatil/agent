#!/usr/bin/env python3
"""
Extract from multiple bit positions - the fragments are in different bit layers!
"""
import onnx, struct, re

model = onnx.load("challenge_final (1).onnx")

# Extract from ALL bit positions for fc1.weight
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        floats = struct.unpack(f'{len(tensor.raw_data)//4}f', tensor.raw_data)
        
        # Extract from each bit position (0-7)
        for bit_pos in range(8):
            bits = [(struct.unpack('I', struct.pack('f', f))[0] >> bit_pos) & 1 for f in floats]
            extracted = bytes([sum(bits[i+j] << j for j in range(8)) for i in range(0, len(bits), 8) if i+8 <= len(bits)])
            result = extracted.decode('latin-1', errors='ignore')
            
            # Look for HDWGT2 or Kaal{ with different content
            if 'HDWGT2' in result or ('Kaal{' in result and 'l4yers' not in result):
                print(f"\n[BIT {bit_pos}] Found different content!")
                if 'HDWGT2' in result:
                    idx = result.index('HDWGT2')
                    print(result[idx:idx+500])
                if 'Kaal{' in result:
                    idx = result.index('Kaal{')
                    end = result.find('}', idx)
                    if end != -1:
                        print(f"FLAG: {result[idx:end+1]}")
        break

# Try XOR of multiple bit positions
print("\n[*] Trying XOR combinations...")
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        floats = struct.unpack(f'{len(tensor.raw_data)//4}f', tensor.raw_data)
        
        # XOR bit 0 and bit 1
        bits0 = [(struct.unpack('I', struct.pack('f', f))[0] >> 0) & 1 for f in floats]
        bits1 = [(struct.unpack('I', struct.pack('f', f))[0] >> 1) & 1 for f in floats]
        xor_bits = [b0 ^ b1 for b0, b1 in zip(bits0, bits1)]
        
        extracted = bytes([sum(xor_bits[i+j] << j for j in range(8)) for i in range(0, len(xor_bits), 8) if i+8 <= len(xor_bits)])
        result = extracted.decode('latin-1', errors='ignore')
        
        if 'Kaal{' in result:
            idx = result.index('Kaal{')
            print(f"\nXOR(bit0,bit1): {result[idx:idx+200]}")
        
        break

# Check if the garbage bytes encode positions in other tensors
print("\n[*] Analyzing garbage bytes as indices...")
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        floats = struct.unpack(f'{len(tensor.raw_data)//4}f', tensor.raw_data)
        bits = [(struct.unpack('I', struct.pack('f', f))[0] & 1) for f in floats]
        extracted = bytes([sum(bits[i+j] << j for j in range(8)) for i in range(0, len(bits), 8) if i+8 <= len(bits)])
        result = extracted.decode('latin-1', errors='ignore')
        
        if 'Kaal{' in result:
            idx = result.index('Kaal{')
            flag_section = result[idx:idx+300]
            
            # Extract the garbage bytes
            match = re.search(r'Kaal\{l4yers_of_d3c03pt10n_m(.{30})@sk', flag_section)
            if match:
                garbage = match.group(1).encode('latin-1')
                print(f"Garbage bytes: {[b for b in garbage[:20]]}")
                
                # These might be tensor indices and byte positions
                # Try interpreting as: tensor_idx, byte_pos pairs
                for i in range(0, min(20, len(garbage)), 2):
                    if i+1 < len(garbage):
                        t_idx = garbage[i] % 14  # 14 tensors
                        b_pos = garbage[i+1]
                        print(f"  Pair {i//2}: tensor={t_idx}, byte={b_pos}")
        break
