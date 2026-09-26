#!/usr/bin/env python3
"""
Use fc2 or head weights as a mask/selector to filter the flag from fc1
The "chord" might mean fc2 tells us WHICH positions in fc1 to read
"""

import onnx
import struct

model = onnx.load(r"D:\mission-git-hackss\challenge_final (3).onnx")

# Extract tensors
tensors = {}
for tensor in model.graph.initializer:
    if tensor.HasField('raw_data'):
        raw = tensor.raw_data
        num_floats = len(raw) // 4
        floats = struct.unpack(f'{num_floats}f', raw)
        tensors[tensor.name] = floats

fc1 = tensors['fc1.weight']
fc2 = tensors['fc2.weight']
head = tensors['head.weight']

print(f"[*] fc1: {len(fc1)} floats")
print(f"[*] fc2: {len(fc2)} floats")
print(f"[*] head: {len(head)} floats")

# Strategy: Use fc2 to select which bytes from fc1 to keep
# Extract LSB from fc1
fc1_bits = []
for f in fc1:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    fc1_bits.append(int_repr & 1)

fc1_bytes = []
for i in range(0, len(fc1_bits), 8):
    if i + 8 <= len(fc1_bits):
        byte_val = sum(fc1_bits[i+j] << j for j in range(8))
        fc1_bytes.append(byte_val)

# Find the flag region
flag_start = None
for i in range(len(fc1_bytes) - 5):
    if fc1_bytes[i:i+5] == [ord('K'), ord('a'), ord('a'), ord('l'), ord('{')]:
        # Check if it's not the decoy
        if i + 20 < len(fc1_bytes):
            chunk = bytes(fc1_bytes[i:i+20])
            if b'1f_TiMe' not in chunk:
                flag_start = i
                break

if flag_start is None:
    print("[-] Could not find flag start")
    exit(1)

flag_end = flag_start
for i in range(flag_start, min(flag_start + 500, len(fc1_bytes))):
    if fc1_bytes[i] == ord('}'):
        flag_end = i + 1
        break

print(f"\n[*] Flag region: bytes {flag_start} to {flag_end}")
print(f"[*] Flag length: {flag_end - flag_start} bytes")

# Now use fc2 as a selector
# Convert fc2 to a selector pattern
fc2_selector = []
for f in fc2:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    # Use LSB as selector bit
    fc2_selector.append(int_repr & 1)

# Convert to byte-level selector
fc2_byte_selector = []
for i in range(0, len(fc2_selector), 8):
    if i + 8 <= len(fc2_selector):
        # If any bit in this byte is 1, select this byte
        has_one = any(fc2_selector[i:i+8])
        fc2_byte_selector.append(has_one)

print(f"\n[*] FC2 selector has {len(fc2_byte_selector)} byte positions")
print(f"[*] FC2 selector has {sum(fc2_byte_selector)} positions marked as 1")

# Apply selector to flag region
print("\n[*] Applying FC2 selector to flag region...")

filtered_bytes = []
for i in range(flag_start, flag_end):
    selector_idx = i % len(fc2_byte_selector)
    byte_val = fc1_bytes[i]
    
    # If selector says to keep this byte, and it's printable, keep it
    if fc2_byte_selector[selector_idx] and 32 <= byte_val < 127:
        filtered_bytes.append(byte_val)
    elif byte_val in [ord('K'), ord('a'), ord('l'), ord('{'), ord('}'), ord('_')]:
        # Always keep flag structure characters
        filtered_bytes.append(byte_val)

filtered_flag = bytes(filtered_bytes)
print(f"  Filtered: {filtered_flag}")

# Try inverse - keep where selector is 0
print("\n[*] Trying inverse selector (keep where FC2=0)...")

filtered_bytes2 = []
for i in range(flag_start, flag_end):
    selector_idx = i % len(fc2_byte_selector)
    byte_val = fc1_bytes[i]
    
    # If selector is 0, keep printable bytes
    if not fc2_byte_selector[selector_idx] and 32 <= byte_val < 127:
        filtered_bytes2.append(byte_val)
    elif byte_val in [ord('K'), ord('a'), ord('l'), ord('{'), ord('}'), ord('_')]:
        filtered_bytes2.append(byte_val)

filtered_flag2 = bytes(filtered_bytes2)
print(f"  Filtered: {filtered_flag2}")

# Try using head as selector
print("\n[*] Using HEAD as selector...")

head_selector = []
for f in head:
    int_repr = struct.unpack('I', struct.pack('f', f))[0]
    head_selector.append(int_repr & 1)

head_byte_selector = []
for i in range(0, len(head_selector), 8):
    if i + 8 <= len(head_selector):
        has_one = any(head_selector[i:i+8])
        head_byte_selector.append(has_one)

filtered_bytes3 = []
for i in range(flag_start, flag_end):
    selector_idx = i % len(head_byte_selector)
    byte_val = fc1_bytes[i]
    
    if head_byte_selector[selector_idx] and 32 <= byte_val < 127:
        filtered_bytes3.append(byte_val)
    elif byte_val in [ord('K'), ord('a'), ord('l'), ord('{'), ord('}'), ord('_')]:
        filtered_bytes3.append(byte_val)

filtered_flag3 = bytes(filtered_bytes3)
print(f"  Filtered: {filtered_flag3}")

print("\n[*] Done")
