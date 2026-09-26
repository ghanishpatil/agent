#!/usr/bin/env python3
"""
Extract and decode the flag from position 9623 where we found "Kaal"
"""

def extract_flag():
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
    
    # Position 9623 has the pattern [1216, 1280, 1280, 1264, 5776]
    # which decodes to "Kaal{"
    
    # Extract the sequence starting from position 9623
    start_pos = 9623
    sequence_length = 100  # Get enough to capture the full flag
    
    gap_sequence = gaps[start_pos:start_pos+sequence_length]
    print(f"\n[*] Gap sequence from position {start_pos}:")
    print(f"    {gap_sequence[:20]}")
    
    # The pattern shows: 1216='K', 1280='a', 1280='a', 1264='l', 5776='{'
    # Let's build a mapping based on this
    
    # First, let's see what unique gaps we have in this region
    from collections import Counter
    gap_counts = Counter(gaps)
    
    # Create initial mapping from the known pattern
    mapping = {
        1216: 'K',
        1280: 'a',
        1264: 'l',
        5776: '{'
    }
    
    # Now we need to figure out the rest of the alphabet
    # Let's look at the most common gaps and try to map them
    print(f"\n[*] Attempting to decode with known pattern:")
    
    # Try to decode the sequence
    decoded = []
    for gap in gap_sequence:
        if gap in mapping:
            decoded.append(mapping[gap])
        else:
            decoded.append('?')
    
    text = ''.join(decoded)
    print(f"    Decoded: {text}")
    
    # Now let's try to figure out the rest by looking at common patterns
    # The flag format is Kaal{...} so we need to find '}'
    
    # Let's look at all unique gaps in the sequence
    unique_gaps_in_seq = set(gap_sequence)
    print(f"\n[*] Unique gaps in this sequence: {sorted(unique_gaps_in_seq)}")
    
    # Try to extend the mapping by analyzing the full gap distribution
    # and common letter frequencies
    
    # Let's try a different approach - look at the actual bytes at these positions
    print(f"\n[*] Trying different decoding approaches:")
    
    # Method: Divide gaps by a constant
    for divisor in [16, 32, 64, 80]:
        decoded = []
        for gap in gap_sequence:
            char_code = gap // divisor
            if 32 <= char_code < 127:
                decoded.append(chr(char_code))
            else:
                decoded.append('?')
        
        text = ''.join(decoded)
        if 'Kaal{' in text and '}' in text:
            print(f"\n[!!!] Divisor {divisor} FOUND COMPLETE FLAG:")
            start = text.index('Kaal{')
            end = text.index('}', start) + 1
            print(f"    {text[start:end]}")
            return
        elif 'Kaal{' in text:
            print(f"    Divisor {divisor}: {text[:80]}")

if __name__ == "__main__":
    extract_flag()
