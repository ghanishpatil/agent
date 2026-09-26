#!/usr/bin/env python3

# The hex at 0x145a is:
# 4c62626d7b42736648ba607a707622486675488945d0488955d848b8224866752267346c48ba3422663162687d

hex_string = "4c62626d7b42736648ba607a707622486675488945d0488955d848b8224866752267346c48ba3422663162687d"

print("[*] Manual hex parsing...")
print(f"  Hex: {hex_string}")

# Convert to bytes
data = bytes.fromhex(hex_string)

# Known x64 assembly opcodes to skip:
# 48 = REX.W prefix
# 89 = MOV
# 45 = part of MOV
# ba = MOV edx, imm32
# b8 = MOV eax, imm32
# d0, d8, c0, c8 = various registers

assembly_bytes = {0x48, 0x89, 0x45, 0xba, 0xb8, 0xd0, 0xd8, 0xc0, 0xc8, 0x55}

# Extract only non-assembly printable bytes
flag_chars = []
i = 0
while i < len(data):
    b = data[i]
    
    # Skip known assembly patterns
    if b in assembly_bytes:
        i += 1
        continue
    
    # Include printable ASCII
    if 32 <= b < 127:
        flag_chars.append(chr(b))
    
    i += 1

encrypted = ''.join(flag_chars)
print(f"  Filtered: {encrypted}")

# Apply ROT25
decrypted = ''
for c in encrypted:
    if c.isalpha():
        if c.islower():
            decrypted += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
        else:
            decrypted += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
    else:
        decrypted += c

print(f"  ROT25: {decrypted}")

# Now let's try a different approach - maybe the flag is constructed differently
# Let me look at the hex byte by byte:

print("\n[*] Byte-by-byte analysis:")
for i in range(0, len(data), 16):
    chunk = data[i:i+16]
    hex_str = ' '.join([f'{b:02x}' for b in chunk])
    ascii_str = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])
    print(f"  {i:04x}: {hex_str:48} | {ascii_str}")

# Let me manually extract based on the pattern:
# 4c62626d7b427366 = "Lbbm{Bsf"
# 48 = H (assembly)
# ba = assembly
# 607a7076 = "`zpv"
# 22 = "
# 486675 = "Hfu" but 48 is assembly, so "fu"
# ...

print("\n[*] Manual extraction of string parts:")
parts = [
    bytes.fromhex("4c62626d7b427366"),  # Lbbm{Bsf
    bytes.fromhex("607a7076"),           # `zpv
    bytes.fromhex("6675"),               # fu
    bytes.fromhex("67346c"),             # g4l
    bytes.fromhex("663162687d"),         # f1bh}
]

for part in parts:
    s = part.decode('latin1')
    print(f"  {part.hex():20} = {s}")

# Concatenate
encrypted_manual = ''.join([p.decode('latin1') for p in parts])
print(f"\n  Concatenated: {encrypted_manual}")

# Apply ROT25
decrypted_manual = ''
for c in encrypted_manual:
    if c.isalpha():
        if c.islower():
            decrypted_manual += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
        else:
            decrypted_manual += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
    else:
        decrypted_manual += c

print(f"  ROT25: {decrypted_manual}")

# Hmm, still has ` and other chars. Let me check if there's a pattern
# Maybe the actual flag is simpler and I'm overthinking

# Let me try to find if there's another string in the binary
print("\n[*] Searching for other potential flags in the binary...")

exe = r".\challenge_mystery\crackme.exe"
with open(exe, 'rb') as f:
    full_data = f.read()

# Search for "Kaal{" directly
if b'Kaal{' in full_data:
    idx = full_data.find(b'Kaal{')
    print(f"  Found 'Kaal{{' at 0x{idx:x}!")
    context = full_data[idx:idx+50]
    print(f"  {context}")
else:
    print("  No direct 'Kaal{' found")

# Maybe the flag is constructed at runtime?
# Let me check if there are multiple encrypted pieces

print("\n[*] Looking for all ROT25-encoded 'Kaal' patterns...")
# "Kaal" in ROT1 (reverse of ROT25) is "Lbbm"
for i in range(len(full_data) - 4):
    if full_data[i:i+4] == b'Lbbm':
        print(f"  Found 'Lbbm' at 0x{i:x}")
        context = full_data[i:i+60]
        # Try to extract a clean string
        clean = ''
        for b in context:
            if 32 <= b < 127 and b not in [0x48, 0x89, 0x45, 0xba, 0xb8]:
                clean += chr(b)
            elif clean and chr(b) not in string.printable:
                break
        
        if '{' in clean and len(clean) > 10:
            # Apply ROT25
            dec = ''
            for c in clean:
                if c.isalpha():
                    if c.islower():
                        dec += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
                    else:
                        dec += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
                else:
                    dec += c
            
            if 'Kaal{' in dec:
                print(f"    Encrypted: {clean}")
                print(f"    Decrypted: {dec}")

import string
