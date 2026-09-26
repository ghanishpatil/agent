#!/usr/bin/env python3
"""
Final attempt to extract the flag text
"""
from PIL import Image
import numpy as np
import re

print("="*60)
print("FINAL TEXT EXTRACTION")
print("="*60)

# Read the binary image with best contrast
img = Image.open('binary_cropped_autoleveled.jpg')
img_array = np.array(img)

print(f"Image size: {img_array.shape}")

# The image should now have clear text
# Let's try to extract it row by row

print("\n[Extracting text row by row]")

# Sample every few rows to find text
for y in range(0, img_array.shape[0], 50):
    row = img_array[y, :]
    
    # Count transitions from black to white (indicates text)
    transitions = 0
    for x in range(1, len(row)):
        if row[x] > 200 and row[x-1] < 50:
            transitions += 1
    
    # If there are many transitions, this row likely has text
    if transitions > 10:
        print(f"\nRow {y} has {transitions} transitions (likely text)")
        
        # Try to extract the text by looking at pixel patterns
        # For now, just show the row
        text_pixels = row > 200
        print(f"    Pattern: {''.join(['#' if p else '.' for p in text_pixels[::10]])}")

# Try a different approach - look for the word "Kaal" in the image
# by checking for specific pixel patterns
print("\n[Searching for 'Kaal{' pattern]")

# The letters would appear as groups of white pixels
# Let's look for 4 distinct groups (K, a, a, l) followed by a brace

# Scan horizontally for groups of white pixels
for y in range(0, img_array.shape[0], 20):
    row = img_array[y, :]
    
    # Find groups of consecutive white pixels
    groups = []
    in_group = False
    group_start = 0
    
    for x in range(len(row)):
        if row[x] > 200:  # White pixel
            if not in_group:
                group_start = x
                in_group = True
        else:  # Black pixel
            if in_group:
                groups.append((group_start, x))
                in_group = False
    
    # If we have 4-6 groups in a row, it might be "Kaal{"
    if 4 <= len(groups) <= 10:
        # Check if groups are reasonably spaced (like letters)
        avg_spacing = np.mean([groups[i+1][0] - groups[i][1] for i in range(len(groups)-1)])
        if 5 < avg_spacing < 100:
            print(f"\nRow {y}: Found {len(groups)} letter-like groups")
            print(f"    Average spacing: {avg_spacing:.1f} pixels")
            print(f"    Groups: {groups[:10]}")

# Let's also try to just read the entire image as a string
# by converting white pixels to characters
print("\n[Converting image to ASCII art]")
for y in range(0, min(200, img_array.shape[0]), 10):
    line = ''
    for x in range(0, min(1000, img_array.shape[1]), 5):
        if img_array[y, x] > 200:
            line += '#'
        else:
            line += ' '
    
    if '#' in line:
        print(line)

print("\n" + "="*60)
print("The flag should be visible in the binary images!")
print("Open binary_cropped_autoleveled.jpg to see it")
print("="*60)
