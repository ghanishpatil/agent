#!/usr/bin/env python3
"""
Helper script to combine flag pieces found from different social media platforms
"""

import re

def combine_flag_pieces():
    """
    Manually enter flag pieces found from different platforms
    """
    print("="*70)
    print("RAVEN CHALLENGE - FLAG PIECE COMBINER")
    print("="*70)
    print("\nEnter flag pieces as you find them from social media.")
    print("Press Enter with empty input when done.\n")
    
    pieces = []
    platform_pieces = {}
    
    while True:
        platform = input(f"Platform #{len(pieces)+1} (e.g., Instagram, Twitter, or press Enter to finish): ").strip()
        if not platform:
            break
        
        piece = input(f"Flag piece from {platform}: ").strip()
        if piece:
            pieces.append(piece)
            platform_pieces[platform] = piece
            print(f"[+] Added piece from {platform}: {piece}\n")
    
    if not pieces:
        print("[!] No pieces entered.")
        return
    
    print("\n" + "="*70)
    print("COLLECTED PIECES:")
    print("="*70)
    for platform, piece in platform_pieces.items():
        print(f"{platform}: {piece}")
    
    print("\n" + "="*70)
    print("POSSIBLE FLAG COMBINATIONS:")
    print("="*70)
    
    # Try different combinations
    # 1. Simple concatenation
    flag1 = ''.join(pieces)
    print(f"1. Direct concatenation: {flag1}")
    
    # 2. With Kaal{} wrapper if not present
    if not flag1.startswith('Kaal{'):
        flag2 = f"Kaal{{{flag1}}}"
        print(f"2. With Kaal wrapper: {flag2}")
    
    # 3. Reverse order
    flag3 = ''.join(reversed(pieces))
    print(f"3. Reverse order: {flag3}")
    
    # 4. Sorted alphabetically
    flag4 = ''.join(sorted(pieces))
    print(f"4. Sorted: {flag4}")
    
    # 5. Check if pieces already contain Kaal{ parts
    if any('Kaal{' in p for p in pieces):
        # Remove Kaal{ and } from all pieces and recombine
        cleaned = []
        for p in pieces:
            p = p.replace('Kaal{', '').replace('}', '')
            cleaned.append(p)
        flag5 = f"Kaal{{''.join(cleaned)}}"
        print(f"5. Cleaned and combined: {flag5}")
    
    print("\n" + "="*70)
    print("Try submitting these flags to the CTF platform!")
    print("="*70)

def decode_common_encodings(text):
    """Try common encoding schemes"""
    import base64
    
    print(f"\n[*] Trying to decode: {text}")
    
    # Base64
    try:
        decoded = base64.b64decode(text).decode('utf-8')
        print(f"[+] Base64: {decoded}")
    except:
        pass
    
    # Hex
    try:
        decoded = bytes.fromhex(text).decode('utf-8')
        print(f"[+] Hex: {decoded}")
    except:
        pass
    
    # ROT13
    try:
        import codecs
        decoded = codecs.decode(text, 'rot_13')
        print(f"[+] ROT13: {decoded}")
    except:
        pass

if __name__ == "__main__":
    combine_flag_pieces()
    
    print("\n" + "="*70)
    print("NEED TO DECODE SOMETHING?")
    print("="*70)
    decode_input = input("Enter text to try common decodings (or press Enter to skip): ").strip()
    if decode_input:
        decode_common_encodings(decode_input)
