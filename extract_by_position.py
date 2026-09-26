#!/usr/bin/env python3
"""
Extract byte at position N from tensor N
"each whisper remembers its place"
"""

import onnx
import struct

model = onnx.load("challenge_final (1).onnx")

# Try different starting positions
for start_pos in [0, 100, 200, 500, 1000]:
    print(f"\n[*] Trying starting position {start_pos}")
    
    flag_bytes = []
    
    for idx, tensor in enumerate(model.graph.initializer):
        if not tensor.HasField('raw_data'):
            continue
        
        raw_data = tensor.raw_data
        num_floats = len(raw_data) // 4
        floats = struct.unpack(f'{num_floats}f', raw_data)
        
        # Extract LSB
        bits = []
        for f in floats:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            bits.append(int_repr & 1)
        
        # Convert to bytes
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
                extracted.append(byte_val)
        
        # Get byte at position (start_pos + idx)
        pos = start_pos + idx
        if pos < len(extracted):
            flag_bytes.append(extracted[pos])
    
    # Convert to string
    flag_attempt = bytes(flag_bytes).decode('latin-1', errors='ignore')
    print(f"  Result: {flag_attempt}")
    
    if 'Kaal{' in flag_attempt:
        print(f"\n[!] FOUND FLAG: {flag_attempt}")
        break
