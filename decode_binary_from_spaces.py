#!/usr/bin/env python3
"""
Decode binary data from space gaps
Small gap = 0, Large gap = 1 (or vice versa)
"""

def decode_binary_from_gaps():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find all space positions
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    
    print(f"[*] Total spaces: {len(space_positions)}")
    
    # Calculate gaps
    gaps = [space_positions[i+1] - space_positions[i] for i in range(len(space_positions)-1)]
    
    # Analyze gap distribution
    from collections import Counter
    gap_counts = Counter(gaps)
    print(f"\n[*] Gap distribution (top 10):")
    for gap, count in gap_counts.most_common(10):
        print(f"    Gap {gap}: {count} times")
    
    # The most common gaps are likely 0 and 1
    # Let's try: 80 = 0, 880 = 1
    print(f"\n[*] Attempting binary decode (80=0, 880=1):")
    
    binary_string = ""
    for gap in gaps:
        if gap == 80:
            binary_string += "0"
        elif gap == 880:
            binary_string += "1"
        else:
            # For other gaps, we'll skip or use a heuristic
            if gap < 500:
                binary_string += "0"
            else:
                binary_string += "1"
    
    print(f"[*] Binary string length: {len(binary_string)} bits")
    print(f"[*] First 200 bits: {binary_string[:200]}")
    
    # Convert binary to ASCII (8 bits per character)
    print(f"\n[*] Decoding as ASCII (8 bits per char):")
    try:
        chars = []
        for i in range(0, len(binary_string), 8):
            if i + 8 <= len(binary_string):
                byte = binary_string[i:i+8]
                char_code = int(byte, 2)
                if 32 <= char_code <= 126:
                    chars.append(chr(char_code))
                else:
                    chars.append('.')
        
        decoded_text = ''.join(chars)
        print(decoded_text[:500])
        
        # Look for flag
        if 'Kaal{' in decoded_text:
            start = decoded_text.find('Kaal{')
            end = decoded_text.find('}', start)
            if end > start:
                flag = decoded_text[start:end+1]
                print(f"\n[!!!] FOUND FLAG: {flag}")
                return flag
    except Exception as e:
        print(f"Error: {e}")
    
    # Try reverse (880=0, 80=1)
    print(f"\n[*] Attempting binary decode (880=0, 80=1):")
    binary_string2 = ""
    for gap in gaps:
        if gap == 880:
            binary_string2 += "0"
        elif gap == 80:
            binary_string2 += "1"
        else:
            if gap < 500:
                binary_string2 += "1"
            else:
                binary_string2 += "0"
    
    try:
        chars = []
        for i in range(0, len(binary_string2), 8):
            if i + 8 <= len(binary_string2):
                byte = binary_string2[i:i+8]
                char_code = int(byte, 2)
                if 32 <= char_code <= 126:
                    chars.append(chr(char_code))
                else:
                    chars.append('.')
        
        decoded_text = ''.join(chars)
        print(decoded_text[:500])
        
        # Look for flag
        if 'Kaal{' in decoded_text:
            start = decoded_text.find('Kaal{')
            end = decoded_text.find('}', start)
            if end > start:
                flag = decoded_text[start:end+1]
                print(f"\n[!!!] FOUND FLAG: {flag}")
                return flag
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    decode_binary_from_gaps()
