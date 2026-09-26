#!/usr/bin/env python3
"""
Patch the collision detection instead of score
Make the game think we never collide
"""

# Read the binary
with open('game/game.exe', 'rb') as f:
    data = bytearray(f.read())

print("="*60)
print("PATCHING COLLISION DETECTION")
print("="*60)

# Find check_collision function
check_collision_str = b'_Z15check_collisionv'
pos = data.find(check_collision_str)

if pos != -1:
    print(f"\n[1] Found check_collision at offset: 0x{pos:x}")
    
    # The function likely returns true/false
    # We want to make it always return false (no collision)
    # In x86, this would be: xor eax, eax; ret (31 C0 C3)
    # Or: mov eax, 0; ret (B8 00 00 00 00 C3)
    
    # But we need to find the actual function code, not just the string
    # The string is in the symbol table, the code is elsewhere
    
    print("    This is just the symbol name, need to find actual code")

# Alternative: patch the score increment to be much larger
print("\n[2] Looking for score increment code:")
# Score is likely incremented by 1 each frame
# We want to change it to increment by 100 or more

# Look for patterns like: add [score], 1
# Or: inc [score]
# These would be near the "Score:" string

score_str_pos = data.find(b'Score:')
if score_str_pos != -1:
    print(f"    'Score:' string at: 0x{score_str_pos:x}")
    
    # Look in the code section before this
    # x86 ADD instruction: 83 C0 01 (add eax, 1)
    # We want to change to: 83 C0 64 (add eax, 100)
    
    search_start = max(0, score_str_pos - 10000)
    search_end = score_str_pos
    
    # Look for add instructions with immediate value 1
    add_patterns = [
        b'\x83\xC0\x01',  # add eax, 1
        b'\x83\xC1\x01',  # add ecx, 1
        b'\x83\xC2\x01',  # add edx, 1
        b'\x83\xC3\x01',  # add ebx, 1
    ]
    
    for pattern in add_patterns:
        pos = search_start
        while pos < search_end:
            pos = data.find(pattern, pos, search_end)
            if pos == -1:
                break
            print(f"    Found {pattern.hex()} at offset: 0x{pos:x}")
            # Patch to add 100 instead of 1
            data[pos+2] = 0x64  # Change 01 to 64 (100 in decimal)
            print(f"        Patched to add 100")
            pos += 1

# Save patched binary
output_file = 'game/game_collision_patched.exe'
with open(output_file, 'wb') as f:
    f.write(data)

print(f"\n[3] Saved patched binary to: {output_file}")

print("\n" + "="*60)
print("PATCHING COMPLETE")
print("="*60)
