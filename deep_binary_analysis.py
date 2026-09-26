#!/usr/bin/env python3
"""
Deep analysis of the game binary to extract the decode algorithm
"""

with open('game/game.exe', 'rb') as f:
    data = f.read()

print("="*80)
print("DEEP BINARY ANALYSIS - FINDING DECODE ALGORITHM")
print("="*80)

# Find the encoded string
encoded_str = b'AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc'
encoded_pos = data.find(encoded_str)

print(f"\n[1] Encoded string at: 0x{encoded_pos:x}")

# Look for "Kaal{" pattern in the binary - this might be the decoded result
kaal_pattern = b'Kaal{'
kaal_positions = []
pos = 0
while True:
    pos = data.find(kaal_pattern, pos)
    if pos == -1:
        break
    kaal_positions.append(pos)
    pos += 1

print(f"\n[2] Found {len(kaal_positions)} occurrences of 'Kaal{{' in binary:")
for pos in kaal_positions:
    # Show context around each occurrence
    context = data[pos:pos+50]
    print(f"   0x{pos:x}: {context}")
    # Try to extract a complete flag
    try:
        end_pos = context.find(b'}')
        if end_pos != -1:
            potential_flag = context[:end_pos+1].decode('utf-8', errors='ignore')
            print(f"      Potential flag: {potential_flag}")
    except:
        pass

# Look for the decode functions d1, d2
print(f"\n[3] Looking for decode function names:")
for func_name in [b'd1', b'd2', b'a1', b'a2', b'a3', b'a4', b'decode', b'decrypt']:
    pos = data.find(func_name)
    if pos != -1:
        print(f"   '{func_name.decode()}' found at: 0x{pos:x}")

# Try to find XOR keys or lookup tables near the encoded string
print(f"\n[4] Analyzing data near encoded string:")
# Check 2KB before and after
window_start = max(0, encoded_pos - 2048)
window_end = min(len(data), encoded_pos + len(encoded_str) + 2048)
window = data[window_start:window_end]

# Look for repeating patterns that might be lookup tables
print(f"   Checking for lookup tables...")

# Base64 alphabet
standard_b64 = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
if standard_b64 in window:
    pos = window.find(standard_b64)
    print(f"   Found standard base64 alphabet at offset: 0x{window_start + pos:x}")

# Custom alphabets
custom_alphabets = [
    b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/',
    b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_',
]

for alpha in custom_alphabets:
    if alpha in window:
        pos = window.find(alpha)
        print(f"   Found custom alphabet at offset: 0x{window_start + pos:x}")
        print(f"      Alphabet: {alpha}")

# Look for the score comparison
print(f"\n[5] Looking for score comparison (0x12C = 300):")
target = 300
# Look for cmp instructions with 0x12C
# In x86: 81 xx 2C 01 00 00 (cmp with immediate 0x12C)
# or: 3D 2C 01 00 00 (cmp eax, 0x12C)
cmp_patterns = [
    b'\x81\x3D' + target.to_bytes(4, 'little'),  # cmp [mem], 0x12C
    b'\x3D' + target.to_bytes(4, 'little'),       # cmp eax, 0x12C
    b'\x81\xF8' + target.to_bytes(4, 'little'),   # cmp eax, 0x12C (alternative)
]

for pattern in cmp_patterns:
    pos = data.find(pattern)
    if pos != -1:
        print(f"   Found score comparison at: 0x{pos:x}")
        # Show surrounding bytes
        context = data[max(0, pos-20):pos+20]
        print(f"      Context: {context.hex()}")

# Try to find any plaintext flags that might be in debug strings
print(f"\n[6] Searching for potential plaintext flags:")
import re
flag_pattern = rb'Kaal\{[A-Za-z0-9_]+\}'
matches = re.findall(flag_pattern, data)
if matches:
    print(f"   Found {len(matches)} potential flags:")
    for match in matches:
        print(f"      {match.decode('utf-8', errors='ignore')}")
else:
    print("   No plaintext flags found")

# Check if there's a simple substitution cipher
print(f"\n[7] Trying simple substitution on encoded string:")
encoded = "AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc"

# Try shifting each character
for shift in range(1, 26):
    result = ''
    for char in encoded:
        if char.isalpha():
            if char.islower():
                result += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            else:
                result += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
        else:
            result += char
    
    if 'kaal' in result.lower() or 'flag' in result.lower():
        print(f"   Shift {shift}: {result}")

print("\n" + "="*80)
