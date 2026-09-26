#!/usr/bin/env python3
"""
Final attempt - try everything systematically
"""

import base64

def final_attempt():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # We know:
    # 1. There are 15066 spaces (0x20)
    # 2. First space at position 15
    # 3. Decoy flag: Kaal{1_th1nk_th15_15_wr0ng}
    # 4. KEY: WRONGKEY (base64: V1JPTkdLRVk=)
    # 5. Hint: "spaces are your friend"
    # 6. Hint: "The challenge starts before the challenge begins"
    
    # Maybe the flag is literally in the first 15 bytes when decoded?
    # Or maybe we need to read every 15th byte?
    
    print(f"[*] Trying to extract every 15th byte:")
    decoded = []
    for i in range(0, min(15000, len(data)), 15):
        byte_val = data[i]
        if 32 <= byte_val < 127:
            decoded.append(chr(byte_val))
        else:
            decoded.append('.')
    
    text = ''.join(decoded)
    print(f"    First 200 chars: {text[:200]}")
    
    if 'Kaal{' in text:
        idx = text.index('Kaal{')
        end_idx = text.find('}', idx)
        if end_idx != -1:
            print(f"\n[!!!] FOUND FLAG: {text[idx:end_idx+1]}")
            return
    
    # Try extracting bytes at positions that are multiples of 15066
    print(f"\n[*] Trying multiples of 15066:")
    for mult in range(1, 10):
        pos = mult * 15066
        if pos < len(data):
            byte_val = data[pos]
            print(f"    Position {pos}: {byte_val} ({chr(byte_val) if 32 <= byte_val < 127 else '?'})")
    
    # Maybe the number 15066 itself is significant?
    # 15066 in ASCII?
    print(f"\n[*] 15066 analysis:")
    print(f"    As hex: {hex(15066)}")
    print(f"    As binary: {bin(15066)}")
    print(f"    Divided by 100: {15066 / 100}")
    print(f"    Divided by 256: {15066 / 256}")
    
    # Try reading the file as if spaces mark boundaries of encoded data
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    
    # Extract all bytes between first and second space
    segment1 = data[space_positions[0]+1:space_positions[1]]
    print(f"\n[*] Segment between first two spaces ({len(segment1)} bytes):")
    print(f"    First 100 bytes (hex): {segment1[:100].hex()}")
    
    # Look for patterns in segment lengths
    segment_lengths = []
    for i in range(len(space_positions)-1):
        length = space_positions[i+1] - space_positions[i] - 1
        segment_lengths.append(length)
    
    print(f"\n[*] First 20 segment lengths: {segment_lengths[:20]}")
    
    # Maybe segment lengths encode the flag?
    decoded = []
    for length in segment_lengths[:100]:
        if 32 <= length < 127:
            decoded.append(chr(length))
        else:
            decoded.append('.')
    
    text = ''.join(decoded)
    print(f"    Decoded from lengths: {text}")
    
    if 'Kaal{' in text:
        idx = text.index('Kaal{')
        end_idx = text.find('}', idx)
        if end_idx != -1:
            print(f"\n[!!!] FOUND FLAG: {text[idx:end_idx+1]}")

if __name__ == "__main__":
    final_attempt()
