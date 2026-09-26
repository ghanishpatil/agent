#!/usr/bin/env python3
"""
Rethink the challenge completely
"The challenge starts before the challenge begins" - what comes BEFORE?
"""

def analyze_everything():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"[*] File size: {len(data)} bytes")
    print(f"[*] First 100 bytes (hex): {data[:100].hex()}")
    print(f"[*] First 100 bytes (text): {data[:100]}")
    
    # The hint: "The challenge starts before the challenge begins"
    # Maybe the flag is in the FIRST 15 bytes before the first space?
    
    # Or maybe it's in the ZIP file name or metadata?
    # Original file: "chall_media (1).zip"
    
    # Let's look for any text strings in the file
    print(f"\n[*] Searching for readable strings:")
    
    # Extract all printable ASCII strings of length 5+
    strings = []
    current_string = []
    
    for byte in data:
        if 32 <= byte < 127:  # Printable ASCII
            current_string.append(chr(byte))
        else:
            if len(current_string) >= 5:
                strings.append(''.join(current_string))
            current_string = []
    
    # Add last string if any
    if len(current_string) >= 5:
        strings.append(''.join(current_string))
    
    print(f"[*] Found {len(strings)} strings of length 5+")
    
    # Look for strings containing "Kaal" or flag-like patterns
    for s in strings:
        if 'Kaal' in s or 'kaal' in s.lower() or '{' in s:
            print(f"    Interesting: {s[:100]}")
    
    # Check the decoy flag we found earlier
    print(f"\n[*] Decoy flag at end: {data[-100:].decode('latin-1', errors='ignore')}")
    
    # Maybe the real flag is XORed or encoded somehow?
    # Let's try XORing the decoy flag with different keys
    
    decoy = b'Kaal{1_th1nk_th15_15_wr0ng}'
    
    print(f"\n[*] Trying to decode the decoy flag:")
    print(f"    Decoy: {decoy}")
    
    # Maybe we need to look at the SPACES themselves as a pattern
    # 15066 spaces - that's a lot!
    
    # Let's check if the NUMBER of spaces means something
    print(f"\n[*] Number of spaces: 15066")
    print(f"    In hex: {hex(15066)}")
    print(f"    In binary: {bin(15066)}")
    
    # Try converting to ASCII
    # 15066 / 100 = 150.66 - not useful
    # 15066 / 256 = 58.8... - not useful
    
    # Maybe the spaces form a visual pattern?
    # Or maybe we need to look at the POSITIONS of spaces differently?
    
    # Let's check the FIRST occurrence of each unique gap value
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    gaps = []
    for i in range(1, len(space_positions)):
        gap = space_positions[i] - space_positions[i-1]
        gaps.append(gap)
    
    # Get first occurrence of each unique gap
    first_occurrences = {}
    for i, gap in enumerate(gaps):
        if gap not in first_occurrences:
            first_occurrences[gap] = i
    
    print(f"\n[*] Unique gaps: {len(first_occurrences)}")
    
    # Maybe the flag is encoded in the ORDER of first occurrences?
    sorted_by_first = sorted(first_occurrences.items(), key=lambda x: x[1])
    
    print(f"\n[*] First 20 gaps in order of first occurrence:")
    for gap, pos in sorted_by_first[:20]:
        print(f"    Position {pos}: gap {gap}")

if __name__ == "__main__":
    analyze_everything()
