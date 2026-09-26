#!/usr/bin/env python3
"""
The first 15 bytes before the first space might be the key
RIFX47ªWAVEfmt - let's decode this in different ways
"""

def decode_first_bytes():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # First 15 bytes
    first_15 = data[:15]
    print(f"[*] First 15 bytes:")
    print(f"    Hex: {first_15.hex()}")
    print(f"    Raw: {first_15}")
    print(f"    As text: {first_15.decode('latin-1')}")
    
    # Try different interpretations
    print(f"\n[*] Byte values: {list(first_15)}")
    
    # Maybe "47" in "RIFX47" is a clue?
    # Or the 0xaa byte?
    
    # Let's check what comes after position 15 (after first space)
    print(f"\n[*] Bytes 16-100:")
    segment = data[16:100]
    print(f"    Hex: {segment.hex()}")
    print(f"    As text: {segment.decode('latin-1', errors='ignore')}")
    
    # Check if "47" or 0xaa is significant
    print(f"\n[*] Looking for pattern with 47 or 0xaa:")
    
    # Maybe we need to XOR with something?
    # Try XORing the file with 0xaa
    print(f"\n[*] Trying XOR with 0xaa on first 100 bytes:")
    xored = bytes([b ^ 0xaa for b in data[:100]])
    print(f"    As text: {xored.decode('latin-1', errors='ignore')}")
    
    if b'Kaal{' in xored:
        print(f"[!!!] Found flag pattern in XOR!")
    
    # Try XOR with 0x47
    print(f"\n[*] Trying XOR with 0x47 on first 100 bytes:")
    xored = bytes([b ^ 0x47 for b in data[:100]])
    print(f"    As text: {xored.decode('latin-1', errors='ignore')}")
    
    if b'Kaal{' in xored:
        print(f"[!!!] Found flag pattern in XOR!")
    
    # Maybe the spaces divide the file into segments and we need to read
    # specific bytes from each segment?
    print(f"\n[*] Extracting first byte from each space-delimited segment:")
    
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    
    # Get first byte after each space
    chars = []
    for i in range(min(200, len(space_positions))):
        pos = space_positions[i]
        if pos + 1 < len(data):
            byte_val = data[pos + 1]
            if 32 <= byte_val < 127:
                chars.append(chr(byte_val))
    
    text = ''.join(chars)
    print(f"    First byte after each space: {text[:100]}")
    
    if 'Kaal{' in text:
        start = text.index('Kaal{')
        end = text.index('}', start) + 1
        print(f"\n[!!!] FOUND FLAG: {text[start:end]}")

if __name__ == "__main__":
    decode_first_bytes()
