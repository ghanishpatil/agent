#!/usr/bin/env python3
"""
Try to extract or reconstruct the flag from the game binary
Since we can't run it easily, let's analyze the decode logic
"""

# Read the binary
with open('game/game.exe', 'rb') as f:
    data = f.read()

print("="*80)
print("EXTRACTING FLAG FROM GAME BINARY")
print("="*80)

# Find the encoded string
encoded_str = b'AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc'
pos = data.find(encoded_str)

print(f"\n[1] Encoded string found at offset: 0x{pos:x}")

# Look for nearby code that might be the decode function
# Check 1KB before and after
context_before = data[max(0, pos-1024):pos]
context_after = data[pos:min(len(data), pos+1024)]

print(f"\n[2] Looking for decode patterns near the string...")

# Look for function calls or references
# In x86/x64, function calls are often: E8 xx xx xx xx (call relative)
# or FF 15 xx xx xx xx (call indirect)

import re

# Find all potential function calls in the context
call_pattern = rb'\xE8....|\xFF\x15....'
calls_before = list(re.finditer(call_pattern, context_before))
calls_after = list(re.finditer(call_pattern, context_after))

print(f"   Found {len(calls_before)} potential calls before string")
print(f"   Found {len(calls_after)} potential calls after string")

# Look for the fetch_flag function
fetch_flag_str = b'fetch_flag'
fetch_pos = data.find(fetch_flag_str)
print(f"\n[3] fetch_flag string at offset: 0x{fetch_pos:x}")

# Look for "Fetching flag" string
fetching_str = b'Fetching flag'
fetching_pos = data.find(fetching_str)
print(f"[4] 'Fetching flag' string at offset: 0x{fetching_pos:x}")

# The decode might use a simple algorithm
# Let's try to find patterns in the binary data we got from base64

print("\n[5] Analyzing the base64-decoded bytes:")
import base64

# The most promising decode (with _ as /)
decoded_bytes = b'\x00\x01\xca\x84\xdf\xd6\xa9\x97\xa5q\xbbg\x8e \xfa\xf0\xe3j\xbf#^\xe9\x9e\xd3Dg'
print(f"   Decoded bytes: {decoded_bytes.hex()}")
print(f"   Length: {len(decoded_bytes)}")

# Try XOR with different keys
print("\n[6] Trying XOR decode on the base64 result:")
for key in range(256):
    try:
        xored = bytes([b ^ key for b in decoded_bytes])
        # Check if it looks like text
        if all(32 <= b < 127 or b in [9, 10, 13] for b in xored):
            decoded_str = xored.decode('utf-8', errors='ignore')
            if 'Kaal{' in decoded_str or len(decoded_str) > 10:
                print(f"   Key 0x{key:02x}: {decoded_str}")
    except:
        pass

# Try XOR with repeating key
print("\n[7] Trying multi-byte XOR keys:")
common_keys = [
    b'key',
    b'flag',
    b'game',
    b'Kaal',
    b'\x00\x01',
    b'\xff\xff',
]

for key in common_keys:
    try:
        xored = bytes([decoded_bytes[i] ^ key[i % len(key)] for i in range(len(decoded_bytes))])
        if all(32 <= b < 127 or b in [9, 10, 13] for b in xored):
            decoded_str = xored.decode('utf-8', errors='ignore')
            if 'Kaal{' in decoded_str or len(decoded_str) > 10:
                print(f"   Key {key}: {decoded_str}")
    except:
        pass

# The first two bytes are 0x00 0x01 - this might be a length prefix
print("\n[8] Interpreting as length-prefixed data:")
if len(decoded_bytes) >= 2:
    length = int.from_bytes(decoded_bytes[:2], 'little')
    print(f"   Length prefix (little-endian): {length}")
    length_be = int.from_bytes(decoded_bytes[:2], 'big')
    print(f"   Length prefix (big-endian): {length_be}")
    
    if length < len(decoded_bytes):
        payload = decoded_bytes[2:2+length]
        print(f"   Payload: {payload.hex()}")
        print(f"   As string: {payload}")

print("\n" + "="*80)
print("SUMMARY:")
print("The flag is encoded with a custom algorithm in the game.")
print("Without running the game or fully reverse engineering the decode function,")
print("we cannot easily extract the flag.")
print("\nOptions:")
print("1. Run the patched game.exe (if you have Windows)")
print("2. Use a disassembler (IDA/Ghidra) to reverse the decode function")
print("3. Use a debugger to step through the decode process")
print("="*80)
