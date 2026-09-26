#!/usr/bin/env python3
"""
Analyze the main.jpeg image for clues about the bubble revolution company
"""
from PIL import Image
import os

# Check if image exists
image_path = "main.jpeg"
if os.path.exists(image_path):
    img = Image.open(image_path)
    print(f"Image size: {img.size}")
    print(f"Image mode: {img.mode}")
    print(f"Image format: {img.format}")
    
    # Check EXIF data
    exif_data = img._getexif()
    if exif_data:
        print("\nEXIF Data:")
        for tag, value in exif_data.items():
            print(f"  {tag}: {value}")
    else:
        print("\nNo EXIF data found")
    
    # Save info
    img.info
    if img.info:
        print("\nImage Info:")
        for key, value in img.info.items():
            print(f"  {key}: {value}")
else:
    print(f"Image not found at {image_path}")
