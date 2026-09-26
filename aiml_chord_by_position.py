#!/usr/bin/env python3
"""
"Each whisper remembers its place" - extract from the SAME positions
across different bit layers and combine them like a chord
"""

import onnx
import struct

model = onnx.load(r"D:\mission-git-hackss\challenge_final (3).onnx")

# Extract fc1.weight
fc1_tensor = None
for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        fc1_tensor = tensor
        break

raw_data = fc1_tensor.raw_data
num_floats = len(raw_data) // 4
floats = struct.unpack(f'{num_floats}f', raw_data)

# Extract from all bit positions
all_bits = []
for bit_pos in range(8):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append((int_repr >> bit_pos) & 1)
    all_bits.append(bits)

# Convert each bit layer to bytes
all_bytes = []
for bits in all_bits:
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    all_bytes.append(bytes(extracted))

# Find the flag position in bit 0
flag_start = all_bytes[0].find(b'Kaal{l4yers')
flag_end = all_bytes[0].find(b'pO1s0ns}', flag_start) + 8

print(f"[*] Flag spans bytes {flag_start} to {flag_end} in bit 0")
print(f"[*] Flag length: {flag_end - flag_start} bytes")

# Now extract the same byte range from all bit positions
print("\n[*] Extracting same byte range from all bit positions:")

for bit_pos in range(8):
    chunk = all_bytes[bit_pos][flag_start:flag_end]
    # Show printable characters
    printable = bytes([b if 32 <= b < 127 else ord('.') for b in chunk])
    print(f"\n[Bit {bit_pos}]: {printable[:100]}")
    
    # Check if this bit has a cleaner version
    if b'Kaal{' in chunk:
        # Try to extract the full flag
        kaal_start = chunk.find(b'Kaal{')
        kaal_end = chunk.find(b'}', kaal_start)
        if kaal_end != -1:
            potential_flag = chunk[kaal_start:kaal_end+1]
            # Check if it's mostly printable
            printable_count = sum(1 for b in potential_flag if 32 <= b < 127)
            if printable_count / len(potential_flag) > 0.8:
                print(f"  [+] Potential clean flag: {potential_flag}")

# Try combining bits at each position
print("\n" + "="*60)
print("[*] Trying to combine bits at each byte position (chord)")
print("="*60)

# For each byte position in the flag range, combine bits from different layers
reconstructed = []
for byte_pos in range(flag_start, flag_end):
    # Get the byte value from each bit layer at this position
    byte_values = [all_bytes[bit_pos][byte_pos] for bit_pos in range(8)]
    
    # Try different combination strategies
    # Strategy 1: Take the most common printable byte
    printable_bytes = [b for b in byte_values if 32 <= b < 127]
    if printable_bytes:
        # Use the first printable one
        reconstructed.append(printable_bytes[0])
    else:
        # Use bit 0 as default
        reconstructed.append(byte_values[0])

reconstructed_flag = bytes(reconstructed)
print(f"\n[Strategy 1 - First printable]: {reconstructed_flag}")

# Strategy 2: Majority voting for each bit
print("\n[Strategy 2 - Majority voting per bit]:")
reconstructed2 = []
for byte_pos in range(flag_start, flag_end):
    # For each bit position in the byte, take majority vote across layers
    result_byte = 0
    for bit_in_byte in range(8):
        votes = []
        for layer in range(8):
            byte_val = all_bytes[layer][byte_pos]
            bit_val = (byte_val >> bit_in_byte) & 1
            votes.append(bit_val)
        
        # Majority vote
        if sum(votes) >= 4:
            result_byte |= (1 << bit_in_byte)
    
    reconstructed2.append(result_byte)

reconstructed_flag2 = bytes(reconstructed2)
print(f"  {reconstructed_flag2}")

# Strategy 3: XOR combination
print("\n[Strategy 3 - XOR all layers]:")
reconstructed3 = []
for byte_pos in range(flag_start, flag_end):
    xor_result = 0
    for layer in range(8):
        xor_result ^= all_bytes[layer][byte_pos]
    reconstructed3.append(xor_result)

reconstructed_flag3 = bytes(reconstructed3)
print(f"  {reconstructed_flag3}")

print("\n[*] Done")
