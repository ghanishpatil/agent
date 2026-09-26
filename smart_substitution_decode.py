#!/usr/bin/env python3
"""
Smart substitution cipher decode
Use the known "Kaal{" pattern at position 9623 to build the cipher
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
    
    print(f"[*] Total gaps: {len(gaps)}")
    
    # At position 9623, we have: [1216, 1280, 1280, 1264, 5776]
    # This should be "Kaal{"
    
    # Build initial mapping
    mapping = {
        1216: 'K',
        1280: 'a',
        1264: 'l',
        5776: '{'
    }
    
    print(f"\n[*] Initial mapping from position 9623:")
    print(f"    1216 -> 'K'")
    print(f"    1280 -> 'a'")
    print(f"    1264 -> 'l'")
    print(f"    5776 -> '{{'")
    
    # Now let's find what gap represents '}'
    # It should be somewhere after position 9623
    
    # Let's decode a large section and look for patterns
    start = 9623
    length = 500
    
    decoded = []
    for i in range(start, min(start + length, len(gaps))):
        gap = gaps[i]
        if gap in mapping:
            decoded.append(mapping[gap])
        else:
            decoded.append('?')
    
    text = ''.join(decoded)
    print(f"\n[*] Decoded text from position {start}:")
    print(f"    {text[:200]}")
    
    # Look for patterns - the flag should have underscores, numbers, letters
    # Common gaps that might be other characters
    from collections import Counter
    gap_counts = Counter(gaps)
    
    print(f"\n[*] Most common gaps (top 40):")
    for i, (gap, count) in enumerate(gap_counts.most_common(40)):
        char = mapping.get(gap, '?')
        print(f"    {i+1}. Gap {gap}: {count} times -> '{char}'")
    
    # Let's try to map more characters based on frequency
    # In English: e, t, a, o, i, n, s, h, r, d, l, c, u, m, w, f, g, y, p, b
    # But we already have 'a' and 'l'
    
    # Common characters in CTF flags: _, {, }, numbers, lowercase letters
    
    # Let's look for the closing brace - it should be a gap that appears
    # relatively rarely and comes after the opening brace
    
    # Find all gaps that appear after 5776 in the sequence starting at 9623
    gaps_after_open = []
    found_open = False
    for i in range(start, min(start + length, len(gaps))):
        if gaps[i] == 5776:
            found_open = True
        elif found_open:
            gaps_after_open.append(gaps[i])
    
    # Look for a gap that might be '}'
    # It should be relatively uncommon
    unique_gaps_after = set(gaps_after_open)
    print(f"\n[*] Unique gaps after opening brace: {len(unique_gaps_after)}")
    
    # Try common gaps for '}'
    for test_gap in [5968, 6394, 6436, 6528, 6736, 6752]:
        if test_gap in unique_gaps_after:
            test_mapping = mapping.copy()
            test_mapping[test_gap] = '}'
            
            decoded = []
            for i in range(start, min(start + length, len(gaps))):
                gap = gaps[i]
                decoded.append(test_mapping.get(gap, '?'))
            
            text = ''.join(decoded)
            if 'Kaal{' in text and '}' in text:
                flag_start = text.index('Kaal{')
                flag_end = text.index('}', flag_start) + 1
                potential_flag = text[flag_start:flag_end]
                print(f"\n[*] Testing gap {test_gap} as '}}': {potential_flag[:50]}")

if __name__ == "__main__":
    decode_flag()
