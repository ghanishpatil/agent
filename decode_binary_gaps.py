#!/usr/bin/env python3
"""
Decode flag from gaps as binary encoding
Common gaps might represent binary 0 and 1
"""

def decode_binary_gaps():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find all space positions
    space_positions = []
    for i, byte in enumerate(data):
        if byte == 0x20:  # space character
            space_positions.append(i)
    
    # Calculate gaps
    gaps = []
    for i in range(1, len(space_positions)):
        gap = space_positions[i] - space_positions[i-1]
        gaps.append(gap)
    
    print(f"[*] Total gaps: {len(gaps)}")
    
    # Try different binary encoding schemes
    # Most common gap (64) = 0, others = 1?
    print("\n[*] Method 1: Gap 64 = 0, others = 1")
    binary_str = ''.join('0' if g == 64 else '1' for g in gaps)
    decode_binary(binary_str, "Method 1")
    
    # Try: small gaps = 0, large gaps = 1
    print("\n[*] Method 2: Gap <= 100 = 0, Gap > 100 = 1")
    binary_str = ''.join('0' if g <= 100 else '1' for g in gaps)
    decode_binary(binary_str, "Method 2")
    
    # Try: Gap 64 = 0, Gap 560/400/960 = 1
    print("\n[*] Method 3: Gap 64 = 0, Gap in [560,400,960,880] = 1")
    binary_str = ''.join('0' if g == 64 else ('1' if g in [560, 400, 960, 880] else 'X') for g in gaps)
    # Remove X's
    binary_str = binary_str.replace('X', '')
    decode_binary(binary_str, "Method 3")
    
    # Try: Multiple bits per gap
    print("\n[*] Method 4: Gaps encode multiple bits")
    # Map common gaps to bit patterns
    gap_to_bits = {
        64: '000',
        560: '001',
        400: '010',
        960: '011',
        80: '100',
        896: '101',
        880: '110',
        720: '111'
    }
    
    bits = []
    for g in gaps:
        if g in gap_to_bits:
            bits.append(gap_to_bits[g])
    
    binary_str = ''.join(bits)
    decode_binary(binary_str, "Method 4")

def decode_binary(binary_str, method_name):
    """Try to decode binary string as ASCII"""
    if len(binary_str) < 8:
        return
    
    # Decode as 8-bit ASCII
    chars = []
    for i in range(0, len(binary_str) - 7, 8):
        byte_str = binary_str[i:i+8]
        try:
            char_code = int(byte_str, 2)
            if 32 <= char_code < 127:
                chars.append(chr(char_code))
            else:
                chars.append('.')
        except:
            chars.append('.')
    
    text = ''.join(chars)
    print(f"    First 200 chars: {text[:200]}")
    
    if 'Kaal{' in text:
        start = text.index('Kaal{')
        end = text.index('}', start) + 1
        print(f"\n[!!!] {method_name} FOUND FLAG: {text[start:end]}")
        return True
    
    return False

if __name__ == "__main__":
    decode_binary_gaps()
