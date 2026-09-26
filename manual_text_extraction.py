#!/usr/bin/env python3
"""
Manually extract text from binary image by analyzing pixel patterns
"""
from PIL import Image
import numpy as np

print("="*60)
print("MANUAL TEXT EXTRACTION")
print("="*60)

# Load the best binary image
img = Image.open('binary_cropped_autoleveled.jpg')
img_array = np.array(img)

print(f"Image size: {img_array.shape}")

# Convert to binary (0 or 1)
binary = (img_array > 128).astype(int)

# Find rows with text (rows with white pixels)
text_rows = []
for y in range(binary.shape[0]):
    white_pixels = np.sum(binary[y, :])
    if white_pixels > 10:  # Row has significant white pixels
        text_rows.append(y)

print(f"\nFound {len(text_rows)} rows with text")

if text_rows:
    # Get the bounding box of text
    min_row = min(text_rows)
    max_row = max(text_rows)
    
    # Find columns with text
    text_cols = []
    for x in range(binary.shape[1]):
        white_pixels = np.sum(binary[:, x])
        if white_pixels > 5:
            text_cols.append(x)
    
    if text_cols:
        min_col = min(text_cols)
        max_col = max(text_cols)
        
        print(f"Text bounding box: rows {min_row}-{max_row}, cols {min_col}-{max_col}")
        
        # Extract the text region
        text_region = binary[min_row:max_row+1, min_col:max_col+1]
        
        print(f"Text region size: {text_region.shape}")
        
        # Display as ASCII art
        print("\n[ASCII representation of text region]")
        print("(1 = white pixel, 0 = black pixel)")
        print()
        
        # Sample every few rows and columns to make it readable
        step_y = max(1, text_region.shape[0] // 50)
        step_x = max(1, text_region.shape[1] // 150)
        
        for y in range(0, text_region.shape[0], step_y):
            line = ''
            for x in range(0, text_region.shape[1], step_x):
                if text_region[y, x]:
                    line += '#'
                else:
                    line += ' '
            print(line)
        
        # Try to identify individual characters by finding connected components
        print("\n[Analyzing character positions]")
        
        # Find vertical gaps (spaces between characters)
        col_sums = np.sum(text_region, axis=0)
        
        # Find columns with no white pixels (gaps)
        gaps = []
        in_gap = False
        gap_start = 0
        
        for x in range(len(col_sums)):
            if col_sums[x] == 0:  # Empty column
                if not in_gap:
                    gap_start = x
                    in_gap = True
            else:  # Column has pixels
                if in_gap and x - gap_start > 3:  # Gap is wide enough
                    gaps.append((gap_start, x))
                in_gap = False
        
        print(f"Found {len(gaps)} potential character gaps")
        
        # Extract individual characters
        if gaps:
            chars = []
            prev_end = 0
            
            for gap_start, gap_end in gaps[:20]:  # First 20 characters
                if gap_start > prev_end:
                    char_region = text_region[:, prev_end:gap_start]
                    chars.append(char_region)
                prev_end = gap_end
            
            # Add last character
            if prev_end < text_region.shape[1]:
                char_region = text_region[:, prev_end:]
                chars.append(char_region)
            
            print(f"Extracted {len(chars)} characters")
            
            # Display each character
            print("\n[Individual characters]")
            for i, char in enumerate(chars[:30]):  # First 30 chars
                print(f"\nChar {i}: {char.shape[1]} pixels wide")
                
                # Display character
                step_y = max(1, char.shape[0] // 20)
                step_x = max(1, char.shape[1] // 10)
                
                for y in range(0, char.shape[0], step_y):
                    line = ''
                    for x in range(0, char.shape[1], step_x):
                        if char[y, x]:
                            line += '#'
                        else:
                            line += ' '
                    print(f"  {line}")

print("\n" + "="*60)
