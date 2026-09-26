#!/usr/bin/env python3
"""
Decode flag from space-based steganography
Extract bytes at space positions and after spaces
"""

def analyze_spaces():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find all space positions
    space_positions = []
    for i, byte in enumerate(data):
        if byte == 0x20:  # space character
            space_positions.append(i)
    
    print(f"[*] Found {len(space_positions)} spaces")
    print(f"[*] First 20 space positions: {space_positions[:20]}")
    
    # Try extracting bytes AT each space position (the space itself)
    print("\n[*] Bytes at space positions (first 100):")
    bytes_at_spaces = bytes([data[pos] for pos in space_positions[:100]])
    print(f"    Hex: {bytes_at_spaces.hex()}")
    
    # Try extracting bytes AFTER each space
    print("\n[*] Bytes immediately AFTER spaces (first 100):")
    bytes_after_spaces = bytes([data[pos+1] if pos+1 < len(data) else 0 for pos in space_positions[:100]])
    print(f"    Hex: {bytes_after_spaces.hex()}")
    print(f"    As text: {bytes_after_spaces.decode('latin-1', errors='ignore')}")
    
    # Try extracting bytes BEFORE each space
    print("\n[*] Bytes immediately BEFORE spaces (first 100):")
    bytes_before_spaces = bytes([data[pos-1] if pos > 0 else 0 for pos in space_positions[:100]])
    print(f"    Hex: {bytes_before_spaces.hex()}")
    print(f"    As text: {bytes_before_spaces.decode('latin-1', errors='ignore')}")
    
    # Try all bytes after spaces
    print("\n[*] ALL bytes after spaces:")
    all_bytes_after = bytes([data[pos+1] if pos+1 < len(data) else 0 for pos in space_positions])
    
    # Look for flag pattern
    text = all_bytes_after.decode('latin-1', errors='ignore')
    if 'Kaal{' in text:
        start = text.index('Kaal{')
        end = text.index('}', start) + 1
        print(f"\n[!!!] FOUND FLAG: {text[start:end]}")
    else:
        # Try to find any readable text
        readable = ''.join(c if 32 <= ord(c) < 127 else '.' for c in text)
        print(f"    Readable chars: {readable[:200]}")
        
        # Save to file for analysis
        with open('bytes_after_spaces.bin', 'wb') as f:
            f.write(all_bytes_after)
        print(f"\n[*] Saved all bytes after spaces to bytes_after_spaces.bin")

if __name__ == "__main__":
    analyze_spaces()
