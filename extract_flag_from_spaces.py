#!/usr/bin/env python3
"""
Extract flag from space-based steganography
The first 15 bytes before the first space might contain the flag!
"""

def extract_flag():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # First space is at position 15
    # Extract everything before it
    prepended = data[:15]
    
    print(f"[*] First 15 bytes (before first space):")
    print(f"    Hex: {prepended.hex()}")
    print(f"    Raw: {prepended}")
    
    try:
        text = prepended.decode('utf-8', errors='ignore')
        print(f"    As UTF-8: {text}")
    except:
        pass
    
    try:
        text = prepended.decode('latin-1', errors='ignore')
        print(f"    As Latin-1: {text}")
    except:
        pass
    
    # Check if it contains flag
    if b'Kaal{' in prepended:
        print(f"\n[!!!] FOUND FLAG: {prepended.decode('utf-8', errors='ignore')}")

if __name__ == "__main__":
    extract_flag()
