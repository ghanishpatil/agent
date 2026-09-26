#!/usr/bin/env python3
"""
Deep analysis of main.jpeg for hidden data
"""
from PIL import Image
import binascii

image_path = "main.jpeg"
img = Image.open(image_path)

print("="*60)
print("DEEP IMAGE ANALYSIS")
print("="*60)

# Check for data appended after JPEG
with open(image_path, 'rb') as f:
    data = f.read()
    
    # Find JPEG end marker (FFD9)
    jpeg_end = data.find(b'\xff\xd9')
    if jpeg_end != -1:
        print(f"\nJPEG ends at byte: {jpeg_end + 2}")
        print(f"Total file size: {len(data)}")
        
        if jpeg_end + 2 < len(data):
            extra_data = data[jpeg_end + 2:]
            print(f"\nExtra data found after JPEG: {len(extra_data)} bytes")
            print(f"Extra data (hex): {binascii.hexlify(extra_data[:100])}")
            print(f"Extra data (ascii): {extra_data[:200]}")
        else:
            print("\nNo extra data after JPEG")

# Check image comment from EXIF
print("\n" + "="*60)
print("EXIF COMMENT FIELD:")
print("="*60)
exif = img._getexif()
if exif:
    # Tag 37510 is UserComment
    # Tag 33432 is Copyright
    # Tag 315 is Artist
    for tag_id in [37510, 33432, 315, 40092, 40093, 40094, 40095]:
        if tag_id in exif:
            print(f"Tag {tag_id}: {exif[tag_id]}")

# Check for LSB steganography in pixels
print("\n" + "="*60)
print("LSB ANALYSIS (first 100 pixels):")
print("="*60)
pixels = list(img.getdata())[:100]
lsb_bits = []
for pixel in pixels:
    if isinstance(pixel, tuple):
        for channel in pixel:
            lsb_bits.append(channel & 1)
    else:
        lsb_bits.append(pixel & 1)

# Convert bits to bytes
lsb_bytes = []
for i in range(0, min(len(lsb_bits), 80), 8):
    byte = 0
    for j in range(8):
        if i + j < len(lsb_bits):
            byte = (byte << 1) | lsb_bits[i + j]
    lsb_bytes.append(byte)

lsb_text = bytes(lsb_bytes)
print(f"LSB data (first 10 bytes): {lsb_text[:10]}")
print(f"LSB as text: {lsb_text}")

print("\n" + "="*60)
print("KEY EXIF FIELDS:")
print("="*60)
print(f"Model: {exif.get(272, 'N/A')}")
print(f"Copyright: {exif.get(33432, 'N/A')}")
print(f"Artist: {exif.get(315, 'N/A')}")
print(f"DateTime: {exif.get(36867, 'N/A')}")

# Parse the comment field more carefully
if 'comment' in img.info:
    comment = img.info['comment']
    if isinstance(comment, bytes):
        comment = comment.decode('utf-8', errors='ignore')
    print(f"\nImage Comment: {comment}")
