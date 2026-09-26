#!/usr/bin/env python3
"""
Smart text finder - look for actual readable text patterns
"""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

print("="*80)
print("SMART TEXT FINDER")
print("="*80)

# Load original image
img = Image.open('image_sJM6Gg8.jpg')
print(f"Original image size: {img.size}")

# Try extreme brightness boost
enhancer = ImageEnhance.Brightness(img)
bright = enhancer.enhance(20.0)  # 20x brightness

# Convert to grayscale
gray = bright.convert('L')

# Apply threshold to get pure black and white
threshold = 50
binary = gray.point(lambda x: 255 if x > threshold else 0)

# Save this version
binary.save('extreme_bright_binary.jpg')
print("Saved: extreme_bright_binary.jpg")

# Try with different thresholds
for thresh in [30, 50, 70, 100, 150]:
    binary_t = gray.point(lambda x: 255 if x > thresh else 0)
    binary_t.save(f'binary_thresh_{thresh}.jpg')
    print(f"Saved: binary_thresh_{thresh}.jpg")

# Also try contrast enhancement
enhancer = ImageEnhance.Contrast(img)
contrasted = enhancer.enhance(10.0)
contrasted_gray = contrasted.convert('L')
contrasted_binary = contrasted_gray.point(lambda x: 255 if x > 50 else 0)
contrasted_binary.save('extreme_contrast_binary.jpg')
print("Saved: extreme_contrast_binary.jpg")

# Try edge detection
edges = gray.filter(ImageFilter.FIND_EDGES)
edges_binary = edges.point(lambda x: 255 if x > 10 else 0)
edges_binary.save('edges_binary.jpg')
print("Saved: edges_binary.jpg")

print("\n" + "="*80)
print("Check the generated images - one should show readable text")
print("="*80)
