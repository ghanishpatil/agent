#!/usr/bin/env python3
"""
Patch the game to call fetch_flag immediately on startup
"""

# Read the binary
with open('game/game.exe', 'rb') as f:
    data = bytearray(f.read())

print("="*60)
print("PATCHING TO CALL FETCH_FLAG DIRECTLY")
print("="*60)

# Find the main function or entry point
# In a PE file, we need to find the entry point from the PE header

# PE header starts at offset 0x3C (contains offset to PE signature)
pe_offset_pos = 0x3C
pe_offset = int.from_bytes(data[pe_offset_pos:pe_offset_pos+4], 'little')

print(f"\n[1] PE header at offset: 0x{pe_offset:x}")

# Entry point RVA is at PE_offset + 0x28
entry_point_rva_pos = pe_offset + 0x28
entry_point_rva = int.from_bytes(data[entry_point_rva_pos:entry_point_rva_pos+4], 'little')

print(f"[2] Entry point RVA: 0x{entry_point_rva:x}")

# Find the image base (usually 0x400000 for 32-bit, 0x140000000 for 64-bit)
image_base_pos = pe_offset + 0x34
image_base = int.from_bytes(data[image_base_pos:image_base_pos+8], 'little')

print(f"[3] Image base: 0x{image_base:x}")

# Calculate file offset from RVA
# We need to find which section this RVA belongs to
# Section table starts at PE_offset + 0xF8 (for PE32+)

# For now, let's try a simpler approach
# Find where "Fetching flag..." is printed and patch nearby code

fetching_pos = data.find(b'Fetching flag')
print(f"\n[4] 'Fetching flag' string at: 0x{fetching_pos:x}")

# The fetch_flag function is likely called near where this string is used
# Look for CALL instructions (E8 opcode) near this string

# Search backwards from the string position
search_start = max(0, fetching_pos - 5000)
search_end = fetching_pos

print(f"\n[5] Searching for CALL instructions from 0x{search_start:x} to 0x{search_end:x}")

call_count = 0
for i in range(search_start, search_end):
    if data[i] == 0xE8:  # CALL instruction
        # Extract the relative offset
        offset = int.from_bytes(data[i+1:i+5], 'little', signed=True)
        target = i + 5 + offset
        
        # Check if this might be fetch_flag
        if 0 < target < len(data):
            call_count += 1
            if call_count <= 10:  # Show first 10
                print(f"    CALL at 0x{i:x} -> 0x{target:x}")

# Alternative: Just patch the score check to always succeed
print("\n[6] Alternative: Patch score comparison")
# Look for CMP instruction comparing with 0x12C (300)
# CMP patterns: 81 F9 2C 01 00 00 (cmp ecx, 0x12C)
#               81 F8 2C 01 00 00 (cmp eax, 0x12C)

cmp_patterns = [
    b'\x81\xF9\x2C\x01\x00\x00',  # cmp ecx, 0x12C
    b'\x81\xF8\x2C\x01\x00\x00',  # cmp eax, 0x12C
    b'\x81\xFA\x2C\x01\x00\x00',  # cmp edx, 0x12C
    b'\x81\xFB\x2C\x01\x00\x00',  # cmp ebx, 0x12C
]

for pattern in cmp_patterns:
    pos = data.find(pattern)
    if pos != -1:
        print(f"    Found CMP with 0x12C at offset: 0x{pos:x}")
        print(f"        Pattern: {pattern.hex()}")
        
        # Patch to compare with 0 instead
        data[pos+2:pos+6] = b'\x00\x00\x00\x00'
        print(f"        Patched to compare with 0")

# Save
output_file = 'game/game_direct_flag.exe'
with open(output_file, 'wb') as f:
    f.write(data)

print(f"\n[7] Saved patched binary to: {output_file}")

print("\n" + "="*60)
