#!/usr/bin/env python3
"""
Extract the exact gaps for the flag and try to decode them
"""

def decode_flag():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find space positions and calculate gaps
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    gaps = []
    for i in range(1, len(space_positions)):
        gap = space_positions[i] - space_positions[i-1]
        gaps.append(gap)
    
    # Position 9623 has "Kaal{????a??}"
    # Let's extract the exact sequence
    start = 9623
    
    # The flag is: K a a l { ? ? ? ? a ? ? }
    # Positions:   0 1 2 3 4 5 6 7 8 9 10 11 12
    
    flag_gaps = gaps[start:start+13]
    print(f"[*] Flag gaps: {flag_gaps}")
    
    # Known mappings
    mapping = {
        1216: 'K',
        1280: 'a',
        1264: 'l',
        5776: '{',
        6436: '}'
    }
    
    print(f"\n[*] Decoding each gap:")
    for i, gap in enumerate(flag_gaps):
        char = mapping.get(gap, '?')
        print(f"    Position {i}: gap={gap} -> '{char}'")
    
    # The unknown gaps are at positions 5, 6, 7, 8, 10, 11
    # Gaps: 960, 1968, 368, 1424, 1648, 896
    
    print(f"\n[*] Unknown gaps to decode:")
    unknown_gaps = [960, 1968, 368, 1424, 1648, 896]
    print(f"    {unknown_gaps}")
    
    # Try different decoding schemes
    print(f"\n[*] Trying different decoding methods:")
    
    # Method 1: ASCII (gap / 16)
    print(f"    Method 1 (gap / 16):")
    for gap in unknown_gaps:
        char_code = gap // 16
        if 32 <= char_code < 127:
            print(f"        {gap} -> {char_code} -> '{chr(char_code)}'")
        else:
            print(f"        {gap} -> {char_code} -> (non-printable)")
    
    # Method 2: ASCII (gap / 80)
    print(f"\n    Method 2 (gap / 80):")
    for gap in unknown_gaps:
        char_code = gap // 80
        if 32 <= char_code < 127:
            print(f"        {gap} -> {char_code} -> '{chr(char_code)}'")
        else:
            print(f"        {gap} -> {char_code} -> (non-printable)")
    
    # Method 3: Try common CTF flag characters
    # Flags often have: numbers (0-9), underscore, lowercase letters
    
    # Let's try to map based on relative values
    # Sort the unknown gaps and try to map them to common characters
    sorted_gaps = sorted(set(unknown_gaps))
    print(f"\n    Sorted unique unknown gaps: {sorted_gaps}")
    
    # Try mapping to common flag characters
    common_chars = ['_', 'c', 'd', 'e', 'h', 'i', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'y', '0', '1', '2', '3', '4', '5']
    
    # Let's try a specific mapping based on the gap values
    # Smaller gaps might be earlier in alphabet
    test_mapping = mapping.copy()
    test_mapping[368] = 'd'  # Small gap
    test_mapping[896] = 'h'  # Medium gap
    test_mapping[960] = 'i'  # Medium gap
    test_mapping[1424] = 'n'  # Larger gap
    test_mapping[1648] = 's'  # Larger gap
    test_mapping[1968] = 't'  # Larger gap
    
    decoded = ''.join([test_mapping.get(g, '?') for g in flag_gaps])
    print(f"\n[*] Test decode: {decoded}")
    
    # Try all permutations of common characters
    from itertools import permutations
    
    print(f"\n[*] Trying systematic permutations...")
    
    # Actually, let's just try to find what makes sense
    # The flag structure is: Kaal{????a??}
    # Common CTF flag patterns: Kaal{something_here}
    
    # Let's try: Kaal{sp4c3s_ar3}  (spaces are your friend!)
    test_chars = ['s', 'p', '4', 'c', '3', 's', '_', 'a', 'r', '3']
    # But we already have 'a' at position 9
    
    # Actually looking at the pattern: Kaal{????a??}
    # Positions: K a a l { ? ? ? ? a ? ? }
    #            0 1 2 3 4 5 6 7 8 9 10 11 12
    
    # Let me try: "sp4c3s" before the 'a'
    test_mapping = mapping.copy()
    test_mapping[960] = 's'
    test_mapping[1968] = 'p'
    test_mapping[368] = '4'
    test_mapping[1424] = 'c'
    test_mapping[1648] = '3'
    test_mapping[896] = 's'
    
    decoded = ''.join([test_mapping.get(g, '?') for g in flag_gaps])
    print(f"    Trying 'sp4c3s': {decoded}")

if __name__ == "__main__":
    decode_flag()
