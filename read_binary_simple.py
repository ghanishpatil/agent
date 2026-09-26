#!/usr/bin/env python3
"""
Simple binary image reader - just show what's there
"""
from PIL import Image
import numpy as np

# Try the extreme bright binary
img = Image.open('extreme_bright_binary.jpg')
arr = np.array(img.convert('L'))

print("Image shape:", arr.shape)

# Convert to pure binary
binary = (arr > 128).astype(int)

# Find the text region
rows_with_text = []
for y in range(binary.shape[0]):
    if np.sum(binary[y, :]) > 50:  # Row has text
        rows_with_text.append(y)

if rows_with_text:
    min_row = min(rows_with_text)
    max_row = max(rows_with_text)
    
    cols_with_text = []
    for x in range(binary.shape[1]):
        if np.sum(binary[:, x]) > 50:
            cols_with_text.append(x)
    
    min_col = min(cols_with_text)
    max_col = max(cols_with_text)
    
    print(f"Text region: rows {min_row}-{max_row}, cols {min_col}-{max_col}")
    
    # Extract and display
    text_region = binary[min_row:max_row+1, min_col:max_col+1]
    
    # Scale down for display
    scale = 0.05  # 5%
    h, w = text_region.shape
    new_h = int(h * scale)
    new_w = int(w * scale)
    
    # Resize using PIL
    text_img = Image.fromarray((text_region * 255).astype(np.uint8))
    text_small = text_img.resize((new_w, new_h), Image.LANCZOS)
    text_small_arr = np.array(text_small)
    text_small_binary = (text_small_arr > 128).astype(int)
    
    print(f"\nScaled size: {text_small_binary.shape}")
    print("\nText visualization:")
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
