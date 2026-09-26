#!/usr/bin/env python3
"""
Try to manually read the flag from the green channel image
"""
from PIL import Image
import numpy as np

# Load the green text cropped image
img = Image.open('green_text_cropped.jpg')
arr = np.array(img.convert('L'))
binary = (arr > 128).astype(int)

print("Image shape:", binary.shape)
print("\nLooking for 'Kaal{' pattern...")

# The flag format is Kaal{}
# Let's look at the top portion of the image where the flag likely starts

# Display top 20% of image at higher resolution
top_portion = binary[:int(binary.shape[0] * 0.2), :]

print(f"Top portion shape: {top_portion.shape}")
print("\nTop portion of image (where flag should start):")
print()

# Display with better resolution
scale = 0.15
h, w = top_portion.shape
new_h = int(h * scale)
new_w = int(w * scale)

top_img = Image.fromarray((top_portion * 255).astype(np.uint8))
top_small = top_img.resize((new_w, new_h), Image.LANCZOS)
top_small_arr = np.array(top_small)
top_small_binary = (top_small_arr > 128).astype(int)

for y in range(top_small_binary.shape[0]):
    line = ''
    for x in range(top_small_binary.shape[1]):
        if top_small_binary[y, x]:
            line += '█'
        else:
            line += ' '
    if '█' in line:
        print(line)

print("\n" + "="*80)
print("The flag text should be visible above.")
print("Look for the pattern 'Kaal{...}'")
print("="*80)

# Also save a high-contrast version
from PIL import ImageEnhance
img_enhanced = ImageEnhance.Contrast(img).enhance(5.0)
img_enhanced.save('green_text_high_contrast.jpg')
print("\nSaved: green_text_high_contrast.jpg (open this in an image viewer)")
