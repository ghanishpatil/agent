#!/usr/bin/env python3
"""
Refine the substitution cipher approach
The gaps seem to encode letters - need to find the right mapping
"""

def refine_substitution():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find space positions and calculate gaps
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    gaps = []
    for i in range(1, len(space_positions)):
        gap = space_positions[i] - space_positions[i-1]
        gaps.append(gap)
    
    print(f"[*] Total gaps: {len(gaps)}")
    
    # Analyze gap distribution
    from collections import Counter
    gap_counts = Counter(gaps)
    
    print(f"\n[*] Top 30 most common gaps:")
    for i, (gap, count) in enumerate(gap_counts.most_common(30)):
        print(f"    {i+1}. Gap {gap}: {count} times")
    
    # Try different character mappings
    # The flag format is Kaal{...}
    # Let's try to find patterns that could spell "Kaal"
    
    print("\n[*] Trying to find 'Kaal{' pattern in gaps:")
    
    # Look for a sequence of 5 gaps that might be "Kaal{"
    # We need to find what gaps correspond to K, a, a, l, {
    
    # Try mapping based on frequency (most common = space or common letter)
    mappings_to_try = [
        # Mapping 1: Top gaps to common letters
        {64: 'a', 560: 'e', 400: 't', 960: 'o', 80: 'i', 896: 'n', 880: 's', 720: 'h', 
         1120: 'r', 336: 'd', 1280: 'l', 368: 'c', 1056: 'u', 496: 'm', 21: 'w', 
         6394: 'f', 43: 'g', 5776: 'y', 36: 'p', 28: 'b', 96709: 'K', 
         240: '{', 320: '}', 160: '_'},
        
        # Mapping 2: Try ASCII-like mapping (gap / 8)
        {},  # Will be computed
        
        # Mapping 3: Direct small gaps to letters
        {64: 'a', 80: 'b', 96: 'c', 112: 'd', 128: 'e', 144: 'f', 160: 'g', 176: 'h',
         192: 'i', 208: 'j', 224: 'k', 240: 'l', 256: 'm', 272: 'n', 288: 'o', 304: 'p'},
    ]
    
    # Try each mapping
    for idx, mapping in enumerate(mappings_to_try):
        if idx == 1:  # Compute ASCII-like mapping
            for gap in set(gaps):
                char_code = gap // 8
                if 32 <= char_code < 127:
                    mapping[gap] = chr(char_code)
        
        decoded = ''.join(mapping.get(g, '?') for g in gaps)
        
        if 'Kaal{' in decoded or 'kaal{' in decoded.lower():
            print(f"\n[!!!] Mapping {idx+1} FOUND FLAG PATTERN!")
            if 'Kaal{' in decoded:
                start = decoded.index('Kaal{')
            else:
                start = decoded.lower().index('kaal{')
            end = decoded.index('}', start) + 1 if '}' in decoded[start:] else start + 100
            print(f"    Flag: {decoded[start:end]}")
            return
        elif 'kaal' in decoded.lower():
            idx_kaal = decoded.lower().index('kaal')
            print(f"    Mapping {idx+1} found 'kaal': {decoded[max(0,idx_kaal-10):idx_kaal+50]}")
    
    # Try to find the pattern by looking at unique gap sequences
    print("\n[*] Looking for unique gap patterns that might be 'Kaal{':")
    
    # Find all 5-gap sequences
    for i in range(len(gaps) - 4):
        seq = gaps[i:i+5]
        # Check if this could be "Kaal{"
        # K and l should be different, a should repeat
        if seq[1] == seq[2] and seq[0] != seq[1] and seq[3] != seq[1]:
            print(f"    Position {i}: {seq} (pattern: X-Y-Y-Z-W)")
            
            # Try to decode with this as "Kaal{"
            test_mapping = {
                seq[0]: 'K',
                seq[1]: 'a',
                seq[2]: 'a',
                seq[3]: 'l',
                seq[4]: '{'
            }
            
            # Extend mapping with common gaps
            for gap, count in gap_counts.most_common(50):
                if gap not in test_mapping:
                    # Assign based on frequency
                    test_mapping[gap] = '?'
            
            decoded = ''.join(test_mapping.get(g, '?') for g in gaps[i:i+100])
            if decoded.startswith('Kaal{'):
                print(f"        Decoded: {decoded}")

if __name__ == "__main__":
    refine_substitution()
