#!/usr/bin/env python3
"""
Search for flag in hex representation
"""

with open(r'D:\mission-git-hackss\flight_record.dat', 'rb') as f:
    data = f.read()

# Kaal{ in hex is 4b 61 61 6c 7b
flag_pattern = b'Kaal{'
flag_pattern_lower = b'kaal{'
flag_pattern_upper = b'KAAL{'

print(f"Searching for flag patterns in {len(data)} bytes...")

# Direct search
if flag_pattern in data:
    idx = data.index(flag_pattern)
    print(f"Found 'Kaal{{' at offset {idx}")
    print(f"Flag: {data[idx:idx+100]}")
elif flag_pattern_lower in data:
    idx = data.index(flag_pattern_lower)
    print(f"Found 'kaal{{' at offset {idx}")
    print(f"Flag: {data[idx:idx+100]}")
elif flag_pattern_upper in data:
    idx = data.index(flag_pattern_upper)
    print(f"Found 'KAAL{{' at offset {idx}")
    print(f"Flag: {data[idx:idx+100]}")
else:
    print("No direct flag pattern found")
    
    # Try with spaces or other separators
    patterns = [
        b'K a a l {',
        b'K_a_a_l_{',
        b'K-a-a-l-{',
        b'K.a.a.l.{',
    ]
    
    for pattern in patterns:
        if pattern in data:
            idx = data.index(pattern)
            print(f"Found pattern {pattern} at offset {idx}")
            print(f"Context: {data[idx:idx+100]}")
            break
    else:
        # Try searching for just "Kaal" without brace
        if b'Kaal' in data:
            idx = data.index(b'Kaal')
            print(f"Found 'Kaal' (no brace) at offset {idx}")
            print(f"Context: {data[idx:idx+100]}")
        else:
            print("No 'Kaal' found at all")
            
            # Print first 1000 bytes as hex
            print("\nFirst 1000 bytes (hex):")
            print(data[:1000].hex())
