#!/usr/bin/env python3
"""
"The challenge starts before the challenge begins"
Maybe we need to extract bytes from the BEGINNING using space positions as indices
"""

def extract_from_beginning():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Get space positions
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    
    print(f"[*] Total spaces: {len(space_positions)}")
    print(f"[*] First 20 space positions: {space_positions[:20]}")
    
    # The first space is at position 15
    # "The challenge starts before the challenge begins"
    # Maybe the flag is in the first 15 bytes?
    
    first_15 = data[:15]
    print(f"\n[*] First 15 bytes: {first_15}")
    print(f"    Hex: {first_15.hex()}")
    print(f"    Text: {first_15.decode('latin-1')}")
    
    # Try different interpretations
    # Maybe it's ROT13 or Caesar cipher?
    
    # Or maybe we use the GAPS as indices into the beginning of the file?
    gaps = []
    for i in range(1, len(space_positions)):
        gap = space_positions[i] - space_positions[i-1]
        gaps.append(gap)
    
    print(f"\n[*] Using gaps as indices into file:")
    
    # Use gaps as byte indices
    decoded = []
    for gap in gaps[:100]:
        if gap < len(data):
            byte_val = data[gap]
            if 32 <= byte_val < 127:
                decoded.append(chr(byte_val))
            else:
                decoded.append('.')
        else:
            decoded.append('?')
    
    text = ''.join(decoded)
    print(f"    First 100 chars: {text}")
    
    if 'Kaal{' in text:
        idx = text.index('Kaal{')
        end_idx = text.find('}', idx)
        if end_idx != -1:
            print(f"\n[!!!] FOUND FLAG: {text[idx:end_idx+1]}")
    
    # Try using gaps modulo some value
    print(f"\n[*] Using gaps % 256 as indices:")
    decoded = []
    for gap in gaps[:200]:
        idx = gap % 256
        if idx < len(data):
            byte_val = data[idx]
            if 32 <= byte_val < 127:
                decoded.append(chr(byte_val))
            else:
                decoded.append('.')
    
    text = ''.join(decoded)
    print(f"    First 200 chars: {text}")
    
    if 'Kaal{' in text:
        idx = text.index('Kaal{')
        end_idx = text.find('}', idx)
        if end_idx != -1:
            print(f"\n[!!!] FOUND FLAG: {text[idx:end_idx+1]}")
    
    # Maybe the flag is encoded in the first N bytes where N = number of unique gaps?
    unique_gaps = len(set(gaps))
    print(f"\n[*] Number of unique gaps: {unique_gaps}")
    print(f"[*] First {unique_gaps} bytes:")
    first_n = data[:unique_gaps]
    print(f"    Hex: {first_n.hex()}")
    print(f"    Text: {first_n.decode('latin-1', errors='ignore')}")

if __name__ == "__main__":
    extract_from_beginning()
