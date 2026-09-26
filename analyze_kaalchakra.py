#!/usr/bin/env python3
"""
Kaalchakra Challenge Analyzer
"""

import requests
from PIL import Image
import hashlib
import io

TARGET_URL = "http://138.199.163.92:12871/"

def download_resources():
    """Download image and script"""
    print("="*60)
    print("Downloading Resources")
    print("="*60)
    
    session = requests.Session()
    
    # Download image.png
    print("\n[*] Downloading image.png...")
    resp = session.get(TARGET_URL + 'image.png')
    if resp.status_code == 200:
        with open('kaalchakra_image.png', 'wb') as f:
            f.write(resp.content)
        print(f"[+] Saved kaalchakra_image.png ({len(resp.content)} bytes)")
        
        # Analyze image
        img = Image.open(io.BytesIO(resp.content))
        print(f"[+] Image size: {img.size}")
        print(f"[+] Image mode: {img.mode}")
    
    # Download script.js
    print("\n[*] Downloading script.js...")
    resp = session.get(TARGET_URL + 'script.js')
    if resp.status_code == 200:
        with open('kaalchakra_script.js', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print(f"[+] Saved kaalchakra_script.js ({len(resp.text)} bytes)")
        print("\n[*] Script content:")
        print(resp.text)
    
    # Download style.css
    print("\n[*] Downloading style.css...")
    resp = session.get(TARGET_URL + 'style.css')
    if resp.status_code == 200:
        with open('kaalchakra_style.css', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print(f"[+] Saved kaalchakra_style.css")

def analyze_bonus_image():
    """Analyze the bonus puppy image for hidden data"""
    print("\n" + "="*60)
    print("Analyzing Bonus Image")
    print("="*60)
    
    try:
        img = Image.open('kaalchakra_image.png')
        
        # Check for text in image
        print(f"[*] Image dimensions: {img.size}")
        print(f"[*] Image format: {img.format}")
        print(f"[*] Image mode: {img.mode}")
        
        # Get pixel data
        pixels = img.load()
        width, height = img.size
        
        # Check if there's LSB steganography
        print("\n[*] Checking for LSB steganography...")
        
        # Extract LSBs
        bits = []
        for y in range(height):
            for x in range(width):
                if img.mode == 'RGB':
                    r, g, b = pixels[x, y]
                    bits.append(r & 1)
                    bits.append(g & 1)
                    bits.append(b & 1)
                elif img.mode == 'RGBA':
                    r, g, b, a = pixels[x, y]
                    bits.append(r & 1)
                    bits.append(g & 1)
                    bits.append(b & 1)
        
        # Convert bits to bytes
        bytes_data = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte = 0
                for j in range(8):
                    byte = (byte << 1) | bits[i + j]
                bytes_data.append(byte)
        
        # Try to decode as text
        try:
            text = bytes(bytes_data[:1000]).decode('utf-8', errors='ignore')
            if 'kaal{' in text.lower() or 'flag' in text.lower():
                print(f"\n[!!!] Found text in LSB: {text[:500]}")
        except:
            pass
        
        # Check EXIF data
        print("\n[*] Checking EXIF data...")
        try:
            exif = img._getexif()
            if exif:
                for tag, value in exif.items():
                    print(f"  {tag}: {value}")
        except:
            print("  No EXIF data")
        
    except Exception as e:
        print(f"[-] Error analyzing image: {e}")

def main():
    download_resources()
    analyze_bonus_image()

if __name__ == "__main__":
    main()
