#!/usr/bin/env python3
"""
Analyze the game binary to find where to patch
"""
import re

# Read the binary
with open('game/game.exe', 'rb') as f:
    data = f.read()

# Search for interesting strings
print("="*60)
print("ANALYZING GAME BINARY")
print("="*60)

# Find "Kaal{" pattern
kaal_pattern = rb'Kaal\{[^}]*\}'
matches = re.findall(kaal_pattern, data)
if matches:
    print("\n[+] Found Kaal{} patterns:")
    for match in matches:
        print(f"    {match}")

# Find score-related strings
score_patterns = [rb'score', rb'Score', rb'SCORE']
for pattern in score_patterns:
    if pattern in data:
        pos = data.find(pattern)
        print(f"\n[+] Found '{pattern.decode()}' at offset: 0x{pos:x}")
        # Show context
        context = data[max(0, pos-50):pos+50]
        print(f"    Context: {context[:100]}")

# Find 0x12C (300 in decimal) as bytes
target_score = 300
# Try different byte representations
representations = [
    target_score.to_bytes(4, 'little'),  # 32-bit little endian
    target_score.to_bytes(4, 'big'),     # 32-bit big endian
    target_score.to_bytes(2, 'little'),  # 16-bit little endian
]

print(f"\n[+] Searching for target score {target_score} (0x{target_score:x}):")
for rep in representations:
    count = data.count(rep)
    if count > 0:
        print(f"    Found {count} occurrences of {rep.hex()}")
        # Find first occurrence
        pos = data.find(rep)
        print(f"    First at offset: 0x{pos:x}")

# Find "fetch_flag" or similar
flag_patterns = [rb'fetch_flag', rb'Fetching flag', rb'flag']
for pattern in flag_patterns:
    if pattern in data:
        pos = data.find(pattern)
        print(f"\n[+] Found '{pattern.decode()}' at offset: 0x{pos:x}")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
