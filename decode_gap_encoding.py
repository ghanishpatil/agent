#!/usr/bin/env python3
"""
Decode flag from gaps between spaces
The gaps might encode ASCII values or binary data
"""

def analyze_gap_encoding():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find all space positions
    space_positions = []
    for i, byte in enumerate(data):
        if byte == 0x20:  # space character
            space_positions.append(i)
    
    print(f"[*] Found {len(space_positions)} spaces")
    
    # Calculate gaps between consecutive spaces
    gaps = []
    for i in range(1, len(space_positions)):
        gap = space_positions[i] - space_positions[i-1]
        gaps.append(gap)
    
    print(f"[*] Total gaps: {len(gaps)}")
    print(f"[*] First 50 gaps: {gaps[:50]}")
    
    # Try interpreting gaps as ASCII values
    print("\n[*] Attempting to decode gaps as ASCII:")
    
    # Method 1: Direct ASCII (gaps as character codes)
    try:
        ascii_chars = ''.join(chr(g) if 32 <= g < 127 else '.' for g in gaps)
        print(f"    Direct ASCII (first 200 chars): {ascii_chars[:200]}")
        
        if 'Kaal{' in ascii_chars:
            start = ascii_chars.index('Kaal{')
            end = ascii_chars.index('}', start) + 1
            print(f"\n[!!!] FOUND FLAG: {ascii_chars[start:end]}")
            return
    except:
        pass
    
    # Method 2: Gaps divided by some constant
    for divisor in [8, 10, 16, 64, 80]:
        try:
            chars = ''.join(chr(g // divisor) if 32 <= g // divisor < 127 else '.' for g in gaps)
            if 'Kaal' in chars or 'kaal' in chars.lower():
                print(f"\n[*] Divisor {divisor} produces readable text:")
                print(f"    {chars[:200]}")
                
                if 'Kaal{' in chars:
                    start = chars.index('Kaal{')
                    end = chars.index('}', start) + 1
                    print(f"\n[!!!] FOUND FLAG: {chars[start:end]}")
                    return
        except:
            pass
    
    # Method 3: Look at unique gap values
    from collections import Counter
    gap_counts = Counter(gaps)
    print(f"\n[*] Most common gaps:")
    for gap, count in gap_counts.most_common(20):
        print(f"    Gap {gap}: {count} times")
    
    # Method 4: Try interpreting as base64 or other encoding
    # Convert gaps to bytes
    gap_bytes = bytes([g % 256 for g in gaps])
    
    # Check for flag pattern
    if b'Kaal{' in gap_bytes:
        text = gap_bytes.decode('latin-1', errors='ignore')
        start = text.index('Kaal{')
        end = text.index('}', start) + 1
        print(f"\n[!!!] FOUND FLAG: {text[start:end]}")
        return
    
    # Save gaps for further analysis
    with open('gaps.txt', 'w') as f:
        f.write('\n'.join(map(str, gaps)))
    print(f"\n[*] Saved gaps to gaps.txt")

if __name__ == "__main__":
    analyze_gap_encoding()
