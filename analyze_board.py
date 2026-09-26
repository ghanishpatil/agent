#!/usr/bin/env python3
"""Analyze board.png for forensics challenge"""
import os
from PIL import Image
import subprocess

IMAGE_PATH = r"D:\mission-git-hackss\board.png"

print("="*80)
print("BOARD.PNG FORENSICS ANALYSIS")
print("="*80)

# Check if file exists
if not os.path.exists(IMAGE_PATH):
    print(f"Error: File not found at {IMAGE_PATH}")
    exit(1)

# Get file info
file_size = os.path.getsize(IMAGE_PATH)
print(f"\nFile: {IMAGE_PATH}")
print(f"Size: {file_size} bytes ({file_size/1024:.2f} KB)")

# Open with PIL
try:
    img = Image.open(IMAGE_PATH)
    print(f"\nImage Info:")
    print(f"  Format: {img.format}")
    print(f"  Mode: {img.mode}")
    print(f"  Size: {img.size[0]}x{img.size[1]}")
    
    # Check for metadata
    if hasattr(img, '_getexif') and img._getexif():
        print(f"\nEXIF Data:")
        exif = img._getexif()
        for tag, value in exif.items():
            print(f"  {tag}: {value}")
    
    # Check image info
    if img.info:
        print(f"\nImage Info Dictionary:")
        for key, value in img.info.items():
            print(f"  {key}: {value}")
            
except Exception as e:
    print(f"Error opening image: {e}")

# Check for hidden data with strings
print("\n[Checking for strings in file]")
try:
    result = subprocess.run(['findstr', '/C:"KAAL" /C:"flag" /C:"FLAG"', IMAGE_PATH], 
                          capture_output=True, text=True, shell=True)
    if result.stdout:
        print("Found strings:")
        print(result.stdout)
except:
    pass

# Check file signature
print("\n[File Signature]")
with open(IMAGE_PATH, 'rb') as f:
    header = f.read(100)
    print(f"First 100 bytes: {header[:100]}")
    
    # Look for flag in raw bytes
    f.seek(0)
    content = f.read()
    if b'KAAL{' in content:
        print("\n*** Found KAAL{ in file! ***")
        start = content.find(b'KAAL{')
        end = content.find(b'}', start)
        if end != -1:
            flag = content[start:end+1].decode('utf-8', errors='ignore')
            print(f"Flag: {flag}")
    elif b'FLAG{' in content:
        print("\n*** Found FLAG{ in file! ***")
        start = content.find(b'FLAG{')
        end = content.find(b'}', start)
        if end != -1:
            flag = content[start:end+1].decode('utf-8', errors='ignore')
            print(f"Flag: {flag}")

print("\n" + "="*80)
print("\nNext steps:")
print("1. Check for steganography (LSB, etc.)")
print("2. Look for hidden data in image channels")
print("3. Check if it's a game board (chess, tic-tac-toe, etc.)")
print("="*80)
