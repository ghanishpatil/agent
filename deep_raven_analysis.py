#!/usr/bin/env python3
"""
Deep analysis of Raven.png since social media accounts don't exist
The flag must be hidden in the image itself
"""

from PIL import Image
import numpy as np
import re

IMAGE_PATH = r"D:\mission-git-hackss\Raven.png"

def extract_all_text_chunks():
    """Extract all text chunks from PNG"""
    print("[*] Extracting all PNG text chunks...")
    
    with open(IMAGE_PATH, 'rb') as f:
        data = f.read()
    
    # Look for text chunks (tEXt, zTXt, iTXt)
    text_patterns = [
        (b'tEXt', 'tEXt'),
        (b'zTXt', 'zTXt'),
        (b'iTXt', 'iTXt'),
    ]
    
    for pattern, name in text_patterns:
        pos = 0
        while True:
            pos = data.find(pattern, pos)
            if pos == -1:
                break
            
            # Extract chunk data
            chunk_start = pos - 4  # Length is 4 bytes before chunk type
            if chunk_start >= 0:
                length = int.from_bytes(data[chunk_start:chunk_start+4], 'big')
                chunk_data = data[pos+4:pos+4+length]
                
                try:
                    # Try to decode as text
                    text = chunk_data.decode('utf-8', errors='ignore')
                    print(f"\n[+] {name} chunk found:")
                    print(f"    {text}")
                    
                    if 'Kaal{' in text:
                        print(f"[!!!] FLAG FOUND: {text}")
                except:
                    pass
            
            pos += 1

def check_lsb_all_channels():
    """Check LSB in all color channels"""
    print("\n[*] Checking LSB in all channels...")
    
    img = Image.open(IMAGE_PATH)
    pixels = np.array(img)
    height, width, channels = pixels.shape
    
    print(f"[*] Image dimensions: {width}x{height}, {channels} channels")
    
    for channel in range(min(channels, 4)):  # RGBA
        channel_names = ['Red', 'Green', 'Blue', 'Alpha']
        print(f"\n[*] Extracting from {channel_names[channel]} channel...")
        
        # Extract LSB
        bits = []
        for y in range(height):
            for x in range(width):
                bits.append(pixels[y, x, channel] & 1)
        
        # Convert to bytes
        bytes_data = []
        for i in range(0, len(bits) - 8, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            bytes_data.append(byte)
        
        # Look for flag
        try:
            text = bytes(bytes_data).decode('utf-8', errors='ignore')
            if 'Kaal{' in text:
                match = re.search(r'Kaal\{[^}]+\}', text)
                if match:
                    print(f"[!!!] FLAG FOUND in {channel_names[channel]}: {match.group()}")
                    return match.group()
            
            # Check first 500 chars for any readable text
            preview = ''.join(chr(b) if 32 <= b < 127 else '.' for b in bytes_data[:500])
            if any(c.isalpha() for c in preview):
                print(f"[*] Preview: {preview[:200]}")
        except:
            pass

def check_pixel_values():
    """Check if pixel values encode data"""
    print("\n[*] Checking pixel value patterns...")
    
    img = Image.open(IMAGE_PATH)
    pixels = np.array(img)
    
    # Check if specific pixels spell out something
    # Try reading diagonal, specific positions, etc.
    
    # Check corners
    corners = [
        (0, 0, "Top-left"),
        (0, pixels.shape[1]-1, "Top-right"),
        (pixels.shape[0]-1, 0, "Bottom-left"),
        (pixels.shape[0]-1, pixels.shape[1]-1, "Bottom-right"),
    ]
    
    print("[*] Corner pixels:")
    for y, x, name in corners:
        print(f"  {name}: {pixels[y, x]}")

def search_for_hidden_data():
    """Search for any hidden data patterns"""
    print("\n[*] Searching for hidden data patterns...")
    
    with open(IMAGE_PATH, 'rb') as f:
        data = f.read()
    
    # Look for Kaal{ anywhere in the file
    if b'Kaal{' in data:
        pos = data.find(b'Kaal{')
        print(f"[!!!] Found 'Kaal{{' at position {pos}")
        
        # Extract surrounding data
        start = max(0, pos - 50)
        end = min(len(data), pos + 200)
        context = data[start:end]
        
        try:
            text = context.decode('utf-8', errors='ignore')
            print(f"[!!!] Context: {text}")
            
            # Try to extract complete flag
            match = re.search(rb'Kaal\{[^}]+\}', data[pos:pos+500])
            if match:
                print(f"[!!!] COMPLETE FLAG: {match.group().decode('utf-8')}")
                return match.group().decode('utf-8')
        except:
            print(f"[*] Raw bytes: {context}")
    
    # Look for base64 encoded data
    import base64
    
    # Check for long base64 strings
    b64_pattern = rb'[A-Za-z0-9+/]{50,}={0,2}'
    matches = re.findall(b64_pattern, data)
    
    for match in matches[:5]:  # Check first 5
        try:
            decoded = base64.b64decode(match)
            if b'Kaal{' in decoded:
                print(f"[!!!] FLAG in base64: {decoded}")
                return decoded.decode('utf-8')
        except:
            pass

def check_exif_and_metadata():
    """Check all possible metadata locations"""
    print("\n[*] Checking all metadata...")
    
    img = Image.open(IMAGE_PATH)
    
    # Check all info
    if hasattr(img, 'info'):
        print("[*] All image info:")
        for key, value in img.info.items():
            print(f"  {key}: {value}")
            if isinstance(value, str) and 'Kaal{' in value:
                print(f"[!!!] FLAG FOUND in {key}: {value}")
                return value
    
    # Check text
    if hasattr(img, 'text'):
        print("[*] Image text:")
        for key, value in img.text.items():
            print(f"  {key}: {value}")
            if 'Kaal{' in value:
                print(f"[!!!] FLAG FOUND in text {key}: {value}")
                return value

def analyze_qr_hint():
    """
    QR says: 'There are 2 season and 5 level!!!'
    Maybe this refers to image properties?
    - 2 seasons = 2 color channels?
    - 5 levels = 5 bit planes?
    """
    print("\n[*] Analyzing '2 seasons and 5 levels' hint...")
    
    img = Image.open(IMAGE_PATH)
    pixels = np.array(img)
    
    # Try extracting from 2 specific channels, 5 bit planes
    print("[*] Trying Red and Green channels (2 seasons), bits 0-4 (5 levels)...")
    
    # Extract bits 0-4 from Red and Green
    for channel_idx, channel_name in [(0, 'Red'), (1, 'Green')]:
        print(f"\n[*] Channel: {channel_name}")
        for bit_plane in range(5):
            print(f"  [*] Bit plane {bit_plane}...")
            
            bits = []
            for y in range(pixels.shape[0]):
                for x in range(pixels.shape[1]):
                    bit = (pixels[y, x, channel_idx] >> bit_plane) & 1
                    bits.append(bit)
            
            # Convert to bytes
            bytes_data = []
            for i in range(0, len(bits) - 8, 8):
                byte = 0
                for j in range(8):
                    byte = (byte << 1) | bits[i + j]
                bytes_data.append(byte)
            
            # Check for flag
            try:
                text = bytes(bytes_data[:1000]).decode('utf-8', errors='ignore')
                if 'Kaal{' in text:
                    match = re.search(r'Kaal\{[^}]+\}', text)
                    if match:
                        print(f"[!!!] FLAG FOUND: {match.group()}")
                        return match.group()
            except:
                pass

if __name__ == "__main__":
    print("="*70)
    print("DEEP RAVEN IMAGE ANALYSIS")
    print("="*70)
    
    flag = None
    
    flag = flag or check_exif_and_metadata()
    flag = flag or extract_all_text_chunks()
    flag = flag or search_for_hidden_data()
    flag = flag or check_lsb_all_channels()
    flag = flag or analyze_qr_hint()
    check_pixel_values()
    
    print("\n" + "="*70)
    if flag:
        print(f"[!!!] FINAL FLAG: {flag}")
    else:
        print("[!] Flag not found in automated analysis")
        print("[*] The flag might require manual steganography tools")
    print("="*70)
