#!/usr/bin/env python3
"""
Complete flag decode with full character mapping
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
    
    # Known mappings from analysis
    mapping = {
        1216: 'K',
        1280: 'a',
        1264: 'l',
        5776: '{',
        6436: '}'
    }
    
    # Now let's try to map the most common gaps to common characters
    # Gap 64 appears 7497 times - likely a very common character
    # In CTF flags, common chars are: _, numbers, lowercase letters
    
    # Let's try different mappings for gap 64
    for test_char in ['_', 'e', 't', 'i', 'n', 's', 'r', 'o', '0', '1', ' ']:
        test_mapping = mapping.copy()
        test_mapping[64] = test_char
        
        # Decode around position 9623
        start = 9623
        length = 100
        
        decoded = []
        for i in range(start, min(start + length, len(gaps))):
            gap = gaps[i]
            decoded.append(test_mapping.get(gap, '?'))
        
        text = ''.join(decoded)
        if 'Kaal{' in text and '}' in text:
            flag_start = text.index('Kaal{')
            flag_end = text.index('}', flag_start) + 1
            potential_flag = text[flag_start:flag_end]
            print(f"Gap 64 = '{test_char}': {potential_flag}")
    
    # Let's also try to map more gaps systematically
    # Try mapping based on ASCII values (gap / 16)
    print(f"\n[*] Trying systematic mapping (gap / 16 = ASCII):")
    
    test_mapping = {}
    for gap in set(gaps):
        char_code = gap // 16
        if 32 <= char_code < 127:
            test_mapping[gap] = chr(char_code)
    
    # Decode around position 9623
    start = 9623
    length = 100
    
    decoded = []
    for i in range(start, min(start + length, len(gaps))):
        gap = gaps[i]
        decoded.append(test_mapping.get(gap, '?'))
    
    text = ''.join(decoded)
    print(f"    {text[:100]}")
    
    if 'Kaal{' in text or 'kaal{' in text.lower():
        print(f"    Found Kaal pattern!")
    
    # Try gap / 80
    print(f"\n[*] Trying gap / 80 = ASCII:")
    test_mapping = {}
    for gap in set(gaps):
        char_code = gap // 80
        if 32 <= char_code < 127:
            test_mapping[gap] = chr(char_code)
    
    decoded = []
    for i in range(start, min(start + length, len(gaps))):
        gap = gaps[i]
        decoded.append(test_mapping.get(gap, '?'))
    
    text = ''.join(decoded)
    print(f"    {text[:100]}")
    
    if 'Kaal{' in text:
        idx = text.index('Kaal{')
        if '}' in text[idx:]:
            end = text.index('}', idx) + 1
            print(f"\n[!!!] FOUND FLAG: {text[idx:end]}")

if __name__ == "__main__":
    decode_flag()
