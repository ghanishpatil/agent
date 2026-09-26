#!/usr/bin/env python3
"""
Patch the game to bypass score check or directly call fetch_flag
Strategy: Change the score requirement from 300 (0x12C) to 0
"""

# Read the binary
with open('game/game.exe', 'rb') as f:
    data = bytearray(f.read())

print("="*60)
print("PATCHING GAME")
print("="*60)

# Find and patch score requirement
# Looking for comparison: cmp score, 0x12C (300)
# We'll change 0x12C to 0x00

target_score = 300
target_bytes = target_score.to_bytes(4, 'little')  # 2c 01 00 00

print(f"\n[1] Searching for score requirement {target_score} (0x{target_score:x})")
print(f"    Looking for bytes: {target_bytes.hex()}")

# Find all occurrences
positions = []
pos = 0
while True:
    pos = data.find(target_bytes, pos)
    if pos == -1:
        break
    positions.append(pos)
    pos += 1

print(f"    Found {len(positions)} occurrences")

# Patch the first few occurrences (likely the score check)
patch_count = 0
for pos in positions[:3]:  # Patch first 3 occurrences
    print(f"\n[2] Patching at offset 0x{pos:x}")
    # Show context before
    context_before = data[pos-10:pos+14]
    print(f"    Before: {context_before.hex()}")
    
    # Patch: change 0x12C (300) to 0x00 (0)
    data[pos:pos+4] = b'\x00\x00\x00\x00'
    
    # Show context after
    context_after = data[pos-10:pos+14]
    print(f"    After:  {context_after.hex()}")
    patch_count += 1

print(f"\n[3] Patched {patch_count} locations")

# Save patched binary
output_file = 'game/game_patched.exe'
with open(output_file, 'wb') as f:
    f.write(data)

print(f"\n[4] Saved patched binary to: {output_file}")

print("\n" + "="*60)
print("PATCHING COMPLETE")
print("="*60)
print("\nNow run: .\\game\\game_patched.exe")
