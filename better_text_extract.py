#!/usr/bin/env python3
"""
Better text extraction with cleaner visualization
"""
from PIL import Image
import numpy as np

print("="*80)
print("BETTER TEXT EXTRACTION")
print("="*80)

# Load the binary image
img = Image.open('binary_cropped_autoleveled.jpg')
img_array = np.array(img)

print(f"Image size: {img_array.shape}")

# Convert to pure binary
binary = (img_array > 128).astype(int)

# Find the actual text region by looking for dense areas
print("\n[Finding text region]")

# Check each row for white pixel density
row_densities = []
for y in range(binary.shape[0]):
    density = np.sum(binary[y, :]) / binary.shape[1]
    row_densities.append(density)

# Find rows with significant text (density > threshold)
threshold = 0.01  # At least 1% white pixels
text_rows = [i for i, d in enumerate(row_densities) if d > threshold]

if text_rows:
    min_row = min(text_rows)
    max_row = max(text_rows)
    
    # Similarly for columns
    col_densities = []
    for x in range(binary.shape[1]):
        density = np.sum(binary[:, x]) / binary.shape[0]
        col_densities.append(density)
    
    text_cols = [i for i, d in enumerate(col_densities) if d > threshold]
    min_col = min(text_cols)
    max_col = max(text_cols)
    
    print(f"Text region: rows {min_row}-{max_row}, cols {min_col}-{max_col}")
    
    # Extract text region
    text_region = binary[min_row:max_row+1, min_col:max_col+1]
    
    # Resize for better viewing (scale down)
    from PIL import Image as PILImage
    text_img = PILImage.fromarray((text_region * 255).astype(np.uint8))
    
    # Scale to reasonable size for ASCII display
    scale = 0.1  # 10% of original
    new_width = int(text_region.shape[1] * scale)
    new_height = int(text_region.shape[0] * scale)
    
    text_img_small = text_img.resize((new_width, new_height), PILImage.LANCZOS)
    text_small = np.array(text_img_small)
    text_small_binary = (text_small > 128).astype(int)
    
    print(f"Scaled text size: {text_small_binary.shape}")
    print("\n[Text visualization (scaled)]")
    print()
    
    # Display as ASCII
    for y in range(text_small_binary.shape[0]):
        line = ''
        for x in range(text_small_binary.shape[1]):
            if text_small_binary[y, x]:
                line += '█'
            else:
                line += ' '
        if '█' in line:  # Only print lines with text
            print(line)
    
    # Try to extract the actual text by looking at horizontal slices
    print("\n" + "="*80)
    print("HORIZONTAL SLICE ANALYSIS")
    print("="*80)
    
    # Look at specific rows that likely contain text
    sample_rows = [
        text_region.shape[0] // 4,
        text_region.shape[0] // 2,
        3 * text_region.shape[0] // 4
    ]
    
    for row_idx in sample_rows:
        print(f"\nRow {row_idx}:")
        row = text_region[row_idx, :]
        
        # Display this row at full resolution
        line = ''
        for x in range(0, len(row), 10):  # Sample every 10 pixels
            if row[x]:
                line += '#'
            else:
                line += ' '
        print(line)

print("\n" + "="*80)
print("Try opening binary_cropped_autoleveled.jpg in an image viewer")
print("The flag should be visible as white text on black background")
print("="*80)
