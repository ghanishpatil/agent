#!/usr/bin/env python3
"""
Decode using the most common gaps: 64 and others
"""

def decode_with_common_gaps():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find all space positions
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    gaps = [space_positions[i+1] - space_positions[i] for i in range(len(space_positions)-1)]
    
    # Most common: 64 (7497 times), then 560, 400, 960
    # Let's try: 64 = 0, anything else = 1
    print("[*] Trying: gap=64 -> 0, gap!=64 -> 1")
    
    binary_string = ""
    for gap in gaps:
        if gap == 64:
            binary_string += "0"
        else:
            binary_string += "1"
    
    print(f"[*] Binary length: {len(binary_string)} bits")
    print(f"[*] First 200 bits: {binary_string[:200]}")
    
    # Decode as ASCII
    chars = []
    for i in range(0, len(binary_string), 8):
        if i + 8 <= len(binary_string):
            byte = binary_string[i:i+8]
            char_code = int(byte, 2)
            if 32 <= char_code <= 126:
                chars.append(chr(char_code))
            else:
                chars.append('.')
    
    decoded = ''.join(chars)
    print(f"\n[*] Decoded text (first 500 chars):")
    print(decoded[:500])
    
    # Search for flag
    if 'Kaal{' in decoded:
        start = decoded.find('Kaal{')
        end = decoded.find('}', start)
        if end > start:
            print(f"\n[!!!] FOUND FLAG: {decoded[start:end+1]}")
            return
    
    # Try reverse
    print("\n" + "="*60)
    print("[*] Trying: gap=64 -> 1, gap!=64 -> 0")
    
    binary_string2 = ""
    for gap in gaps:
        if gap == 64:
            binary_string2 += "1"
        else:
            binary_string2 += "0"
    
    chars = []
    for i in range(0, len(binary_string2), 8):
        if i + 8 <= len(binary_string2):
            byte = binary_string2[i:i+8]
            char_code = int(byte, 2)
            if 32 <= char_code <= 126:
                chars.append(chr(char_code))
            else:
                chars.append('.')
    
    decoded = ''.join(chars)
    print(f"\n[*] Decoded text (first 500 chars):")
    print(decoded[:500])
    
    # Search for flag
    if 'Kaal{' in decoded:
        start = decoded.find('Kaal{')
        end = decoded.find('}', start)
        if end > start:
            print(f"\n[!!!] FOUND FLAG: {decoded[start:end+1]}")
            return
    
    # Print full decoded text to search manually
    print(f"\n[*] Full decoded text:")
    print(decoded)

if __name__ == "__main__":
    decode_with_common_gaps()
