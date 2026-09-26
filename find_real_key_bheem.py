#!/usr/bin/env python3
"""
Find the real key - if there's a WRONGKEY, there must be a RIGHTKEY or CORRECTKEY
"""

import base64

def find_real_key():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Search for other KEY patterns
    print(f"[*] Searching for KEY patterns:")
    
    patterns = [b'KEY', b'RIGHTKEY', b'CORRECTKEY', b'REALKEY', b'TRUEKEY', 
                b'key', b'Key', b'FLAG', b'flag', b'Flag']
    
    for pattern in patterns:
        count = data.count(pattern)
        if count > 0:
            print(f"    Found '{pattern.decode()}': {count} times")
            
            # Find first occurrence
            pos = data.find(pattern)
            if pos != -1:
                context = data[max(0, pos-50):pos+100]
                print(f"        First at {pos}: {context[:150]}")
    
    # Maybe the real flag is encoded with the spaces?
    # Let's try XORing the space positions with "WRONGKEY"
    
    print(f"\n[*] Trying to decode using WRONGKEY as XOR key:")
    
    key = b'WRONGKEY'
    
    # Get bytes at space positions
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    
    # Try XORing bytes after spaces
    decoded = []
    for i, pos in enumerate(space_positions[:100]):
        if pos + 1 < len(data):
            byte_val = data[pos + 1]
            key_byte = key[i % len(key)]
            decoded_byte = byte_val ^ key_byte
            if 32 <= decoded_byte < 127:
                decoded.append(chr(decoded_byte))
            else:
                decoded.append('.')
    
    text = ''.join(decoded)
    print(f"    Decoded (first 100): {text}")
    
    if 'Kaal{' in text:
        print(f"\n[!!!] FOUND FLAG: {text}")
    
    # Try XORing bytes before spaces
    print(f"\n[*] Trying bytes BEFORE spaces:")
    decoded = []
    for i, pos in enumerate(space_positions[:100]):
        if pos > 0:
            byte_val = data[pos - 1]
            key_byte = key[i % len(key)]
            decoded_byte = byte_val ^ key_byte
            if 32 <= decoded_byte < 127:
                decoded.append(chr(decoded_byte))
            else:
                decoded.append('.')
    
    text = ''.join(decoded)
    print(f"    Decoded (first 100): {text}")
    
    if 'Kaal{' in text:
        print(f"\n[!!!] FOUND FLAG: {text}")
    
    # Try XORing the gaps themselves
    print(f"\n[*] Trying to XOR gaps:")
    gaps = []
    for i in range(1, len(space_positions)):
        gap = space_positions[i] - space_positions[i-1]
        gaps.append(gap)
    
    # XOR gap values (as bytes)
    decoded = []
    for i, gap in enumerate(gaps[:100]):
        # Use lower byte of gap
        gap_byte = gap & 0xFF
        key_byte = key[i % len(key)]
        decoded_byte = gap_byte ^ key_byte
        if 32 <= decoded_byte < 127:
            decoded.append(chr(decoded_byte))
        else:
            decoded.append('.')
    
    text = ''.join(decoded)
    print(f"    Decoded (first 100): {text}")
    
    if 'Kaal{' in text:
        print(f"\n[!!!] FOUND FLAG: {text}")

if __name__ == "__main__":
    find_real_key()
