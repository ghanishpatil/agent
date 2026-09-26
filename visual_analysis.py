#!/usr/bin/env python3
"""
Visual analysis - brighten image and look for hidden text
"""
from PIL import Image, ImageEnhance, ImageOps
import numpy as np

image_path = "image_sJM6Gg8.jpg"

print("="*60)
print("VISUAL ANALYSIS")
print("="*60)

img = Image.open(image_path)

# Brighten the image
print("\n[1] Brightening image:")
enhancer = ImageEnhance.Brightness(img)
brightened = enhancer.enhance(10.0)  # Increase brightness by 10x
brightened.save("brightened.jpg")
print("    Saved as brightened.jpg")

# Increase contrast
print("\n[2] Increasing contrast:")
enhancer = ImageEnhance.Contrast(brightened)
contrasted = enhancer.enhance(5.0)
contrasted.save("contrasted.jpg")
print("    Saved as contrasted.jpg")

# Invert colors
print("\n[3] Inverting colors:")
inverted = ImageOps.invert(img.convert('RGB'))
inverted.save("inverted.jpg")
print("    Saved as inverted.jpg")

# Auto-level (stretch histogram)
print("\n[4] Auto-leveling:")
autoleveled = ImageOps.autocontrast(img, cutoff=0)
autoleveled.save("autoleveled.jpg")
print("    Saved as autoleveled.jpg")

# Equalize histogram
print("\n[5] Equalizing histogram:")
equalized = ImageOps.equalize(img)
equalized.save("equalized.jpg")
print("    Saved as equalized.jpg")

# Check if there's text in the enhanced images using OCR
print("\n[6] Attempting OCR on enhanced images:")
try:
    import pytesseract
    
    for name, image in [
        ('original', img),
        ('brightened', brightened),
        ('contrasted', contrasted),
        ('inverted', inverted),
        ('autoleveled', autoleveled),
        ('equalized', equalized)
    ]:
        print(f"\n    {name}:")
        text = pytesseract.image_to_string(image)
        if text.strip():
            print(f"        Text found: {text[:200]}")
            if 'Kaal{' in text:
                import re
                flag = re.search(r'Kaal\{[^}]+\}', text)
                if flag:
                    print(f"\n[+] FLAG FOUND: {flag.group(0)}")
        else:
            print("        No text detected")
            
except ImportError:
    print("    pytesseract not installed")
except Exception as e:
    print(f"    Error: {e}")

# Check pixel values at specific locations (maybe flag is encoded in specific pixels)
print("\n[7] Checking specific pixel locations:")
img_array = np.array(img)

# Check corners
corners = [
    (0, 0, "Top-left"),
    (0, img_array.shape[1]-1, "Top-right"),
    (img_array.shape[0]-1, 0, "Bottom-left"),
    (img_array.shape[0]-1, img_array.shape[1]-1, "Bottom-right"),
]

for y, x, name in corners:
    pixel = img_array[y, x]
    print(f"    {name}: R={pixel[0]}, G={pixel[1]}, B={pixel[2]}")
    
    # Try to interpret as ASCII
    if all(32 <= p < 127 for p in pixel):
        chars = ''.join([chr(p) for p in pixel])
        print(f"        As ASCII: '{chars}'")

print("\n" + "="*60)
print("Check the saved images visually for hidden text!")
print("="*60)
