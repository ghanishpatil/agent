#!/usr/bin/env python3
"""
Extract just the left portion which seems to have the flag
"""
from PIL import Image
import numpy as np

# Load the extreme bright binary
img = Image.open('extreme_bright_binary.jpg')
arr = np.array(img.convert('L'))
binary = (arr > 128).astype(int)

print("Full image shape:", binary.shape)

# The text seems to be in the left portion
# Let's extract just the left 40% of the image
left_portion = binary[:, :int(binary.shape[1] * 0.4)]

print("Left portion shape:", left_portion.shape)

# Find text bounds in left portion
rows_with_text = []
for y in range(left_portion.shape[0]):
    if np.sum(left_portion[y, :]) > 20:
        rows_with_text.append(y)

cols_with_text = []
for x in range(left_portion.shape[1]):
    if np.sum(left_portion[:, x]) > 20:
        cols_with_text.append(x)

if rows_with_text and cols_with_text:
    min_row = min(rows_with_text)
    max_row = max(rows_with_text)
    min_col = min(cols_with_text)
    max_col = max(cols_with_text)
    
    text_region = left_portion[min_row:max_row+1, min_col:max_col+1]
    
    print(f"Text region: {text_region.shape}")
    
    # Save this cropped version
    text_img = Image.fromarray((text_region * 255).astype(np.uint8))
    text_img.save('left_text_only.jpg')
    print("Saved: left_text_only.jpg")
    
    # Display at higher resolution
    scale = 0.15  # 15%
    h, w = text_region.shape
    new_h = int(h * scale)
    new_w = int(w * scale)
    
    text_small = text_img.resize((new_w, new_h), Image.LANCZOS)
    text_small_arr = np.array(text_small)
    text_small_binary = (text_small_arr > 128).astype(int)
    
    print(f"\nScaled size: {text_small_binary.shape}")
    print("\nText (should be readable):")
    print()
    
    for y in range(text_small_binary.shape[0]):
        line = ''
        for x in range(text_small_binary.shape[1]):
            if text_small_binary[y, x]:
                line += '█'
            else:
                line += ' '
        if '█' in line:
            print(line)
