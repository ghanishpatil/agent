#!/usr/bin/env python3

# From the hex dump:
# 4c62626d7b42736648ba607a707622486675488945d0488955d848b8224866752267346c48ba34226631626 87d

# Let me parse this byte by byte
hex_string = "4c62626d7b42736648ba607a707622486675488945d0488955d848b8224866752267346c48ba3422663162687d"

bytes_data = bytes.fromhex(hex_string)

print("[*] Analyzing hex bytes...")
print(f"  Total bytes: {len(bytes_data)}")

# Extract only printable ASCII that looks like part of a flag
flag_chars = []
i = 0
while i < len(bytes_data):
    b = bytes_data[i]
    c = chr(b)
    
    # Check if it's printable and likely part of the flag
    if 32 <= b < 127:
        # Skip if it looks like assembly (common x64 opcodes)
        if b not in [0x48, 0x89, 0x45, 0x55, 0xd0, 0xd8, 0xb8, 0xba]:
            flag_chars.append(c)
    
    i += 1

encrypted_flag = ''.join(flag_chars)
print(f"  Extracted: {encrypted_flag}")

# Apply ROT25
decrypted = ''
for c in encrypted_flag:
    if c.isalpha():
        if c.islower():
            decrypted += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
        else:
            decrypted += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
    else:
        decrypted += c

print(f"  ROT25: {decrypted}")

# Let me also try a smarter approach - look for the pattern
# The hex shows: Lbbm{Bsf then some bytes, then `zpv, then more bytes, etc.

# Manual extraction based on the hex:
# 4c62626d7b427366 = "Lbbm{Bsf"
# 48 = H (assembly)
# ba = separator
# 607a7076 = "`zpv"
# 22 = "
# 486675 = "Hfu" (but 48 is assembly, so "fu")
# ...

# Let me extract sequences between assembly bytes
print("\n[*] Smart extraction - skipping assembly opcodes...")

assembly_opcodes = {0x48, 0x89, 0x45, 0x55, 0xd0, 0xd8, 0xb8, 0xba, 0xc0, 0xc8}

smart_extract = []
for b in bytes_data:
    if b not in assembly_opcodes and 32 <= b < 127:
        smart_extract.append(chr(b))

smart_flag = ''.join(smart_extract)
print(f"  Extracted: {smart_flag}")

# Apply ROT25
smart_decrypted = ''
for c in smart_flag:
    if c.isalpha():
        if c.islower():
            smart_decrypted += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
        else:
            smart_decrypted += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
    else:
        smart_decrypted += c

print(f"  ROT25: {smart_decrypted}")

# The flag should be something like: Kaal{Are_you_...}
# Let me check if this makes sense
if smart_decrypted.startswith('Kaal{') and smart_decrypted.endswith('}'):
    print(f"\n[+] VALID FLAG FORMAT!")
    print(f"[+] FLAG: {smart_decrypted}")
else:
    print(f"\n[*] Flag format doesn't match, trying manual reconstruction...")
    
    # Based on the pieces we saw:
    # Lbbm{Bsf -> Kaal{Are
    # `zpv -> `you
    # fu -> et
    # g4l -> f4k
    # f1bh -> e1ag
    
    # This suggests: Kaal{Are_you_getting_f4ke_fl4g}
    # But let me check the actual bytes more carefully
    
    # Looking at: Lbbm{BsfH`zpv"Hfu"g4lH4"f1bh}
    # Removing H: Lbbm{Bsf`zpv"fu"g4l4"f1bh}
    
    manual = "Lbbm{Bsf_`zpv_fu_g4l_4_f1bh}"
    manual_dec = ''
    for c in manual:
        if c.isalpha():
            if c.islower():
                manual_dec += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
            else:
                manual_dec += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
        else:
            manual_dec += c
    
    print(f"  Manual reconstruction: {manual} -> {manual_dec}")
