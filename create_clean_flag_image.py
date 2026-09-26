#!/usr/bin/env python3
"""
Create the cleanest possible image of the flag
"""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

print("Creating clean flag image...")

# Load original
img = Image.open('image_sJM6Gg8.jpg')

# Extract green channel (has the best signal)
img_array = np.array(img)
green = img_array[:, :, 1]

# Apply aggressive threshold
threshold = 35
binary = (green > threshold).astype(np.uint8) * 255

# Create image
binary_img = Image.fromarray(binary)

# Crop to text region
arr = np.array(binary_img)
rows_with_text = np.where(np.sum(arr > 0, axis=1) > 100)[0]
cols_with_text = np.where(np.sum(arr > 0, axis=0) > 100)[0]

if len(rows_with_text) > 0 and len(cols_with_text) > 0:
    min_row = rows_with_text[0]
    max_row = rows_with_text[-1]
    min_col = cols_with_text[0]
    max_col = cols_with_text[-1]
    
    cropped = binary_img.crop((min_col, min_row, max_col, max_row))
    
    # Save at full resolution
    cropped.save('FLAG_IMAGE.png')
    print("✓ Saved: FLAG_IMAGE.png")
    
    # Also create a zoomed version of the top (where flag starts)
    height = cropped.size[1]
    top_portion = cropped.crop((0, 0, cropped.size[0], height // 3))
    top_portion.save('FLAG_IMAGE_TOP.png')
    print("✓ Saved: FLAG_IMAGE_TOP.png (top portion with flag start)")
    
    print("\n" + "="*80)
    print("OPEN THESE IMAGES IN AN IMAGE VIEWER:")
    print("  1. FLAG_IMAGE.png - Full flag text")
    print("  2. FLAG_IMAGE_TOP.png - Top portion (easier to read)")
    print("\nThe flag should be clearly visible as white text on black background.")
    print("="*80)
else:
    print("Could not find text region")
