#!/usr/bin/env python3
"""
TimoPlayzzz OSINT Investigation Script
Helps investigate the YouTube channel for the flag
"""

import base64
import re

print("="*80)
print("TIMOPLAYZZ OSINT INVESTIGATION")
print("="*80)

print("\n[TARGET]")
print("YouTube Channel: @TimoPlayzzz")
print("URL: https://www.youtube.com/@TimoPlayzzz")
print("Flag Format: Kaal{}")

print("\n[INVESTIGATION STEPS]")
print("\n1. Manual Investigation Required:")
print("   - Open https://www.youtube.com/@TimoPlayzzz in your browser")
print("   - Check the 'About' section for channel description")
print("   - Look at video titles and descriptions")
print("   - Check pinned comments on videos")
print("   - Look for social media links")

print("\n2. Common Flag Locations in YouTube OSINT:")
print("   ✓ Channel About section")
print("   ✓ Video descriptions")
print("   ✓ Pinned comments")
print("   ✓ Community posts")
print("   ✓ Channel banner image (steganography)")
print("   ✓ Profile picture (steganography)")
print("   ✓ Linked social media accounts")

print("\n3. Decoding Functions Available:")
print("   - Base64 decode")
print("   - ROT13")
print("   - Hex to ASCII")
print("   - Binary to text")

def decode_base64(text):
    """Decode base64 text"""
    try:
        decoded = base64.b64decode(text).decode('utf-8')
        return decoded
    except:
        return None

def decode_rot13(text):
    """Decode ROT13 text"""
    result = ''
    for char in text:
        if char.isalpha():
            if char.islower():
                result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
            else:
                result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
        else:
            result += char
    return result

def decode_hex(text):
    """Decode hex to ASCII"""
    try:
        # Remove spaces and 0x prefix if present
        text = text.replace(' ', '').replace('0x', '')
        decoded = bytes.fromhex(text).decode('utf-8')
        return decoded
    except:
        return None

def decode_binary(text):
    """Decode binary to ASCII"""
    try:
        # Remove spaces
        text = text.replace(' ', '')
        # Split into 8-bit chunks
        chars = [text[i:i+8] for i in range(0, len(text), 8)]
        decoded = ''.join([chr(int(char, 2)) for char in chars])
        return decoded
    except:
        return None

def find_flag_pattern(text):
    """Search for Kaal{} pattern in text"""
    pattern = r'Kaal\{[^}]+\}'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches

print("\n[HELPER FUNCTIONS]")
print("\nIf you find suspicious text, you can decode it:")
print("\nExample usage:")
print("  text = 'S2FhbHt0ZXN0X2ZsYWd9'  # Your found text")
print("  decoded = decode_base64(text)")
print("  print(decoded)")

print("\n" + "="*80)
print("INSTRUCTIONS:")
print("="*80)
print("\n1. Open https://www.youtube.com/@TimoPlayzzz in your web browser")
print("\n2. Check these locations in order:")
print("   a) Channel 'About' section - look for description text")
print("   b) Video descriptions - check all videos")
print("   c) Comments - especially pinned comments")
print("   d) Community tab - if available")
print("   e) Social media links - Twitter, Instagram, etc.")
print("\n3. If you find encoded text, use the decode functions above")
print("\n4. Look for the pattern: Kaal{...}")
print("\n5. The flag might be:")
print("   - Plain text in description")
print("   - Base64 encoded")
print("   - Hidden in an image (download banner/profile pic)")
print("   - In a linked social media bio")

print("\n" + "="*80)
print("READY TO INVESTIGATE!")
print("="*80)

# Interactive mode
print("\n[INTERACTIVE DECODER]")
print("If you found suspicious text, paste it here to try decoding:")
print("(Press Ctrl+C to skip)")

try:
    user_input = input("\nPaste text to decode (or press Enter to skip): ").strip()
    
    if user_input:
        print("\n[TRYING DIFFERENT DECODINGS]")
        
        # Try Base64
        b64_result = decode_base64(user_input)
        if b64_result:
            print(f"\nBase64 decode: {b64_result}")
            flags = find_flag_pattern(b64_result)
            if flags:
                print(f"  ✓ FOUND FLAG: {flags[0]}")
        
        # Try ROT13
        rot13_result = decode_rot13(user_input)
        print(f"\nROT13 decode: {rot13_result}")
        flags = find_flag_pattern(rot13_result)
        if flags:
            print(f"  ✓ FOUND FLAG: {flags[0]}")
        
        # Try Hex
        hex_result = decode_hex(user_input)
        if hex_result:
            print(f"\nHex decode: {hex_result}")
            flags = find_flag_pattern(hex_result)
            if flags:
                print(f"  ✓ FOUND FLAG: {flags[0]}")
        
        # Try Binary
        binary_result = decode_binary(user_input)
        if binary_result:
            print(f"\nBinary decode: {binary_result}")
            flags = find_flag_pattern(binary_result)
            if flags:
                print(f"  ✓ FOUND FLAG: {flags[0]}")
        
        # Check if input itself contains flag
        flags = find_flag_pattern(user_input)
        if flags:
            print(f"\n✓ FOUND FLAG IN PLAIN TEXT: {flags[0]}")

except KeyboardInterrupt:
    print("\n\nSkipped interactive mode.")

print("\n" + "="*80)
print("Good luck with your investigation!")
print("="*80)
