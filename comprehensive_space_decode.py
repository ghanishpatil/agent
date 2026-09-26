#!/usr/bin/env python3
"""
Comprehensive decoding attempt - try all reasonable methods
"""

def comprehensive_decode():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find space positions
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    print(f"[*] Found {len(space_positions)} spaces")
    
    # Method 1: Extract bytes at positions that are multiples of space count
    print("\n[*] Method 1: Positions based on space count")
    step = len(data) // len(space_positions)
    chars = []
    for i in range(0, len(data), step):
        if i < len(data):
            byte_val = data[i]
            if 32 <= byte_val < 127:
                chars.append(chr(byte_val))
    
    text = ''.join(chars)
    print(f"    Text: {text}")
    if 'Kaal{' in text:
        print(f"[!!!] FOUND FLAG: {text}")
        return
    
    # Method 2: Use space positions as a cipher - extract from those exact positions
    print("\n[*] Method 2: Bytes at space positions themselves")
    # We know they're all 0x20, so try positions +2, +3, etc.
    for offset in range(2, 10):
        chars = []
        for pos in space_positions[:500]:  # First 500 spaces
            if pos + offset < len(data):
                byte_val = data[pos + offset]
                if 32 <= byte_val < 127:
                    chars.append(chr(byte_val))
                else:
                    chars.append('.')
        
        text = ''.join(chars)
        if 'Kaal{' in text:
            print(f"[!!!] Offset +{offset} FOUND FLAG: {text}")
            return
        elif 'Kaal' in text:
            print(f"    Offset +{offset}: {text[:100]}")
    
    # Method 3: Decode the gaps as a substitution cipher
    print("\n[*] Method 3: Gaps as substitution cipher")
    gaps = []
    for i in range(1, len(space_positions)):
        gap = space_positions[i] - space_positions[i-1]
        gaps.append(gap)
    
    # Map unique gaps to letters
    unique_gaps = sorted(set(gaps))
    print(f"    Found {len(unique_gaps)} unique gap values")
    
    # Try mapping most common gaps to common letters
    from collections import Counter
    gap_counts = Counter(gaps)
    
    # English letter frequency: E T A O I N S H R
    common_letters = 'etaoinshrdlcumwfgypbvkjxqz_{}ETAOINSHRDLCUMWFGYPBVKJXQZ0123456789'
    
    gap_to_char = {}
    for i, (gap, count) in enumerate(gap_counts.most_common()):
        if i < len(common_letters):
            gap_to_char[gap] = common_letters[i]
    
    decoded = ''.join(gap_to_char.get(g, '?') for g in gaps[:500])
    print(f"    Decoded (first 200): {decoded[:200]}")
    
    if 'kaal' in decoded.lower():
        print(f"[!!!] Found 'kaal' in decoded text!")
        idx = decoded.lower().index('kaal')
        print(f"    Context: {decoded[max(0,idx-20):idx+100]}")
    
    # Method 4: XOR consecutive gaps
    print("\n[*] Method 4: XOR consecutive gaps")
    xored_gaps = []
    for i in range(1, len(gaps)):
        xored_gaps.append(gaps[i] ^ gaps[i-1])
    
    chars = []
    for val in xored_gaps[:500]:
        if 32 <= val < 127:
            chars.append(chr(val))
        else:
            chars.append('.')
    
    text = ''.join(chars)
    print(f"    XORed gaps: {text[:200]}")
    if 'Kaal{' in text:
        print(f"[!!!] FOUND FLAG: {text}")

if __name__ == "__main__":
    comprehensive_decode()
