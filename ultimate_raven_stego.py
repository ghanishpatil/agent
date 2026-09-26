#!/usr/bin/env python3
"""
Ultimate steganography analysis for Raven.png
Try every possible technique
"""

from PIL import Image
import numpy as np
import re
import struct

IMAGE_PATH = r"D:\mission-git-hackss\Raven.png"

def check_end_of_file():
    """Check for data appended after PNG IEND chunk"""
    print("[*] Checking for data after IEND chunk...")
    
    with open(IMAGE_PATH, 'rb') as f:
        data = f.read()
    
    # Find IEND chunk
    iend_pos = data.find(b'IEND')
    if iend_pos != -1:
        # IEND chunk is 12 bytes total (4 length + 4 type + 4 CRC)
        after_iend = data[iend_pos + 8:]
        
        if len(after_iend) > 0:
            print(f"[+] Found {len(after_iend)} bytes after IEND!")
            print(f"[*] First 200 bytes: {after_iend[:200]}")
            
            # Try to decode as text
            try:
                text = after_iend.decode('utf-8', errors='ignore')
                print(f"[*] As text: {text[:500]}")
                
                if 'Kaal{' in text:
                    match = re.search(r'Kaal\{[^}]+\}', text)
                    if match:
                        print(f"[!!!] FLAG FOUND: {match.group()}")
                        return match.group()
            except:
                pass

def extract_by_color_pattern():
    """
    '2 seasons and 5 levels' might mean:
    - Extract from 2 specific color channels
    - Using 5 specific bit positions
    """
    print("\n[*] Trying different channel/bit combinations...")
    
    img = Image.open(IMAGE_PATH)
    pixels = np.array(img)
    
    # Try all combinations of 2 channels and 5 bits
    channels = [(0, 1, 'R+G'), (0, 2, 'R+B'), (1, 2, 'G+B'), (0, 3, 'R+A'), (1, 3, 'G+A'), (2, 3, 'B+A')]
    
    for ch1, ch2, name in channels:
        for bits in ['01234', '12345', '23456', '34567']:
            print(f"[*] Trying {name} with bits {bits}...")
            
            extracted = []
            for y in range(pixels.shape[0]):
                for x in range(pixels.shape[1]):
                    # Alternate between channels
                    if (y * pixels.shape[1] + x) % 2 == 0:
                        val = pixels[y, x, ch1]
                    else:
                        val = pixels[y, x, ch2]
                    
                    # Extract specified bits
                    for bit_pos in bits:
                        bit = (val >> int(bit_pos)) & 1
                        extracted.append(bit)
            
            # Convert to bytes
            bytes_data = []
            for i in range(0, min(len(extracted), 10000), 8):
                if i + 8 <= len(extracted):
                    byte = 0
                    for j in range(8):
                        byte = (byte << 1) | extracted[i + j]
                    bytes_data.append(byte)
            
            # Check for flag
            try:
                text = bytes(bytes_data).decode('utf-8', errors='ignore')
                if 'Kaal{' in text:
                    match = re.search(r'Kaal\{[^}]+\}', text)
                    if match:
                        print(f"[!!!] FLAG FOUND with {name} bits {bits}: {match.group()}")
                        return match.group()
            except:
                pass

def check_pixel_differences():
    """Check if adjacent pixels encode data"""
    print("\n[*] Checking pixel differences...")
    
    img = Image.open(IMAGE_PATH)
    pixels = np.array(img)
    
    # Calculate differences between adjacent pixels
    diffs = []
    for y in range(pixels.shape[0] - 1):
        for x in range(pixels.shape[1] - 1):
            # Difference in red channel
            diff = int(pixels[y+1, x, 0]) - int(pixels[y, x, 0])
            diffs.append(diff & 0xFF)
    
    # Look for patterns
    text = ''.join(chr(d) if 32 <= d < 127 else '.' for d in diffs[:1000])
    if 'Kaal{' in text:
        match = re.search(r'Kaal\{[^}]+\}', text)
        if match:
            print(f"[!!!] FLAG FOUND in pixel differences: {match.group()}")
            return match.group()

def check_specific_coordinates():
    """
    Maybe '2 seasons and 5 levels' refers to coordinates?
    Season 2, Level 5 = (2, 5) or (25, 25) etc.
    """
    print("\n[*] Checking specific coordinates...")
    
    img = Image.open(IMAGE_PATH)
    pixels = np.array(img)
    
    coords_to_check = [
        (2, 5), (5, 2), (25, 25), (250, 250), (500, 500),
        (20, 50), (200, 500), (2, 500), (500, 2)
    ]
    
    for x, y in coords_to_check:
        if y < pixels.shape[0] and x < pixels.shape[1]:
            pixel = pixels[y, x]
            print(f"  ({x}, {y}): {pixel}")
            
            # Try to decode pixel values as ASCII
            text = ''.join(chr(p) if 32 <= p < 127 else '.' for p in pixel[:3])
            if text.isprintable():
                print(f"    As text: {text}")

def extract_from_alpha_channel():
    """Specifically check alpha channel"""
    print("\n[*] Deep analysis of alpha channel...")
    
    img = Image.open(IMAGE_PATH)
    if img.mode != 'RGBA':
        print("[!] No alpha channel")
        return
    
    pixels = np.array(img)
    alpha = pixels[:, :, 3]
    
    # Check if alpha has variations
    unique_alpha = np.unique(alpha)
    print(f"[*] Unique alpha values: {unique_alpha}")
    
    if len(unique_alpha) > 1:
        print("[+] Alpha channel has variations!")
        
        # Extract all alpha values as bytes
        alpha_flat = alpha.flatten()
        text = ''.join(chr(a) if 32 <= a < 127 else '.' for a in alpha_flat[:1000])
        
        if 'Kaal{' in text:
            match = re.search(r'Kaal\{[^}]+\}', text)
            if match:
                print(f"[!!!] FLAG FOUND in alpha: {match.group()}")
                return match.group()

def try_xor_patterns():
    """Try XOR with common keys"""
    print("\n[*] Trying XOR patterns...")
    
    with open(IMAGE_PATH, 'rb') as f:
        data = f.read()
    
    # Try XOR with simple keys
    keys = [0xFF, 0xAA, 0x55, 0x42, ord('K'), ord('a'), ord('l')]
    
    for key in keys:
        xored = bytes([b ^ key for b in data[-1000:]])  # Check last 1000 bytes
        
        try:
            text = xored.decode('utf-8', errors='ignore')
            if 'Kaal{' in text:
                match = re.search(r'Kaal\{[^}]+\}', text)
                if match:
                    print(f"[!!!] FLAG FOUND with XOR key {hex(key)}: {match.group()}")
                    return match.group()
        except:
            pass

if __name__ == "__main__":
    print("="*70)
    print("ULTIMATE RAVEN STEGANOGRAPHY ANALYSIS")
    print("="*70)
    
    flag = None
    
    flag = flag or check_end_of_file()
    flag = flag or extract_from_alpha_channel()
    flag = flag or extract_by_color_pattern()
    flag = flag or check_pixel_differences()
    flag = flag or try_xor_patterns()
    check_specific_coordinates()
    
    print("\n" + "="*70)
    if flag:
        print(f"[!!!] FINAL FLAG: {flag}")
    else:
        print("[!] Flag still not found")
        print("[*] The challenge might require:")
        print("    - Actual social media investigation (accounts might be on different platforms)")
        print("    - Specialized steganography tools (steghide, outguess, etc.)")
        print("    - The QR hint might be misleading or metaphorical")
    print("="*70)
