#!/usr/bin/env python3
"""
The hint says "spaces are your friend" - maybe the spaces themselves spell out the flag
when viewed in a specific way, or maybe we need to look at specific positions
"""

def find_flag_pattern():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find all space positions
    space_positions = []
    for i, byte in enumerate(data):
        if byte == 0x20:  # space character
            space_positions.append(i)
    
    print(f"[*] Found {len(space_positions)} spaces")
    print(f"[*] First space at position: {space_positions[0]}")
    print(f"[*] Last space at position: {space_positions[-1]}")
    
    # The hint says "challenge starts before the challenge begins"
    # Maybe we need to look at positions BEFORE the first space?
    # Or maybe at specific intervals?
    
    # Try extracting bytes at regular intervals starting from position 0
    print("\n[*] Trying to extract flag from regular intervals:")
    
    for interval in [15, 16, 32, 64, 80, 100]:
        chars = []
        for i in range(0, min(1000, len(data)), interval):
            byte_val = data[i]
            if 32 <= byte_val < 127:
                chars.append(chr(byte_val))
            else:
                chars.append('.')
        
        text = ''.join(chars)
        if 'Kaal{' in text:
            print(f"\n[!!!] Interval {interval} FOUND FLAG:")
            start = text.index('Kaal{')
            end = text.index('}', start) + 1
            print(f"    {text[start:end]}")
            return
        elif 'Kaal' in text or 'kaal' in text.lower():
            print(f"    Interval {interval}: Found 'Kaal' - {text[:100]}")
    
    # Try extracting from space positions modulo something
    print("\n[*] Trying space positions modulo patterns:")
    
    # Extract every Nth space
    for n in [2, 3, 4, 5, 8, 10, 16, 32, 64]:
        chars = []
        for i in range(0, len(space_positions), n):
            pos = space_positions[i]
            # Try byte before space
            if pos > 0:
                byte_val = data[pos - 1]
                if 32 <= byte_val < 127:
                    chars.append(chr(byte_val))
        
        text = ''.join(chars)
        if 'Kaal{' in text:
            print(f"\n[!!!] Every {n}th space (byte before) FOUND FLAG:")
            start = text.index('Kaal{')
            end = text.index('}', start) + 1
            print(f"    {text[start:end]}")
            return
        elif len(text) > 10 and 'Kaal' in text:
            print(f"    Every {n}th space: {text[:100]}")
    
    # Try looking at the gaps themselves as indices
    print("\n[*] Using gaps as indices into the file:")
    gaps = []
    for i in range(1, min(100, len(space_positions))):
        gap = space_positions[i] - space_positions[i-1]
        gaps.append(gap)
    
    # Use gaps as indices
    chars = []
    for gap in gaps:
        if gap < len(data):
            byte_val = data[gap]
            if 32 <= byte_val < 127:
                chars.append(chr(byte_val))
            else:
                chars.append('.')
    
    text = ''.join(chars)
    print(f"    Using gaps as indices: {text[:100]}")
    if 'Kaal{' in text:
        start = text.index('Kaal{')
        end = text.index('}', start) + 1
        print(f"\n[!!!] FOUND FLAG: {text[start:end]}")

if __name__ == "__main__":
    find_flag_pattern()
