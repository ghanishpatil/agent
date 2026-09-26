#!/usr/bin/env python3
"""
What if fc2 is used to decode/XOR fc1?
"the last whisper waits at fc2" - fc2 is the key
"chord" - combine fc1 and fc2
"""

import onnx
import struct

model = onnx.load("challenge_final (2).onnx")

# Get fc1 and fc2
fc1_data = None
fc2_data = None

for tensor in model.graph.initializer:
    if tensor.name == "fc1.weight":
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        fc1_data = struct.unpack(f'{num_floats}f', raw)
    elif tensor.name == "fc2.weight":
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        fc2_data = struct.unpack(f'{num_floats}f', raw)

print(f"[*] fc1: {len(fc1_data)} floats")
print(f"[*] fc2: {len(fc2_data)} floats")

# Extract LSB from both
def get_lsb_bytes(floats):
    bits = []
    for f in floats:
        int_repr = struct.unpack('I', struct.pack('f', f))[0]
        bits.append(int_repr & 1)
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bits[i+j] << j for j in range(8))
            extracted.append(byte_val)
    return bytes(extracted)

fc1_bytes = get_lsb_bytes(fc1_data)
fc2_bytes = get_lsb_bytes(fc2_data)

print(f"[*] fc1 LSB: {len(fc1_bytes)} bytes")
print(f"[*] fc2 LSB: {len(fc2_bytes)} bytes")

# XOR fc1 with fc2 (repeating fc2 as key)
print(f"\n[*] XORing fc1 with fc2...")
xored = bytearray()
for i in range(len(fc1_bytes)):
    fc2_byte = fc2_bytes[i % len(fc2_bytes)]
    xored.append(fc1_bytes[i] ^ fc2_byte)

result = bytes(xored).decode('latin-1', errors='ignore')

# Look for flag
if 'Kaal{' in result:
    import re
    for match in re.finditer(r'Kaal\{[^\}]*\}', result):
        flag = match.group()
        # Check if clean
        clean = all(32 <= ord(c) < 127 for c in flag)
        if clean:
            print(f"\n[+] CLEAN FLAG FOUND: {flag}")
        else:
            print(f"\n[*] Corrupted flag found: {flag[:50]}...")
else:
    print(f"[-] No Kaal{{ found after XOR")
    # Check readability
    readable = sum(1 for c in result if 32 <= ord(c) < 127)
    print(f"[*] Readable: {readable}/{len(result)} chars")
    if readable > 1000:
        print(f"[*] First 500 chars: {result[:500]}")

print("\n[*] Done")
