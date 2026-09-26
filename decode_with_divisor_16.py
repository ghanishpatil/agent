#!/usr/bin/env python3
"""
Decode gaps by dividing by 16 - this is a common encoding scheme
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
    
    # Try dividing by 16
    print("\n[*] Decoding with divisor 16:")
    decoded = []
    for gap in gaps:
        char_code = gap // 16
        if 32 <= char_code < 127:
            decoded.append(chr(char_code))
        else:
            decoded.append('.')
    
    text = ''.join(decoded)
    
    # Look for flag pattern
    if 'Kaal{' in text:
        print(f"[!!!] FOUND FLAG PATTERN!")
        start = text.index('Kaal{')
        # Find the closing brace
        end_search = text[start:]
        if '}' in end_search:
            end = start + end_search.index('}') + 1
            flag = text[start:end]
            print(f"\n[!!!] FLAG: {flag}")
            return flag
        else:
            # Print a large chunk to see the flag
            print(f"    Flag (first 200 chars): {text[start:start+200]}")
    else:
        print(f"    No 'Kaal{{' found. First 500 chars:")
        print(f"    {text[:500]}")
    
    # Also try other divisors
    for divisor in [8, 12, 20, 24, 32]:
        decoded = []
        for gap in gaps:
            char_code = gap // divisor
            if 32 <= char_code < 127:
                decoded.append(chr(char_code))
            else:
                decoded.append('.')
        
        text = ''.join(decoded)
        if 'Kaal{' in text and '}' in text[text.index('Kaal{'):]:
            print(f"\n[!!!] Divisor {divisor} FOUND FLAG:")
            start = text.index('Kaal{')
            end = text.index('}', start) + 1
            print(f"    {text[start:end]}")
            return

if __name__ == "__main__":
    decode_flag()
