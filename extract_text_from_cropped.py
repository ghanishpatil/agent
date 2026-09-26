#!/usr/bin/env python3
"""
Extract text from the cropped images
"""
from PIL import Image
import numpy as np

print("="*60)
print("EXTRACTING TEXT FROM CROPPED IMAGES")
print("="*60)

for img_name in ['cropped_equalized.jpg', 'cropped_contrasted.jpg', 'cropped_autoleveled.jpg']:
    print(f"\n[{img_name}]")
    
    try:
        img = Image.open(img_name)
        img_array = np.array(img)
        
        print(f"    Size: {img_array.shape}")
        
        # Convert to grayscale for easier analysis
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2).astype(np.uint8)
        else:
            gray = img_array
        
        # Threshold to get binary image (text should be bright)
        threshold = 100
        binary = (gray > threshold).astype(np.uint8) * 255
        
        # Save binary version
        binary_img = Image.fromarray(binary)
        binary_name = f"binary_{img_name}"
        binary_img.save(binary_name)
        print(f"    Saved binary version as {binary_name}")
        
        # Count white pixels (potential text)
        white_pixels = np.sum(binary == 255)
        total_pixels = binary.size
        white_percentage = (white_pixels / total_pixels) * 100
        
        print(f"    White pixels: {white_pixels} ({white_percentage:.2f}%)")
        
        # If there's a reasonable amount of white pixels, there might be text
        if 0.1 < white_percentage < 50:
            print(f"    Potential text detected!")
            
            # Try to find connected components (letters)
            from scipy import ndimage
            labeled, num_features = ndimage.label(binary)
            print(f"    Found {num_features} connected components")
            
            if num_features > 5 and num_features < 1000:
                print(f"    This looks like text! Check {binary_name} visually")
        
    except Exception as e:
        print(f"    Error: {e}")

# Also try to manually read the pixel values in a grid pattern
# Maybe the flag is encoded as pixel values in a specific pattern
print("\n[Checking for encoded message in pixel grid]")
img = Image.open('cropped_equalized.jpg')
img_array = np.array(img)

# Sample pixels in a grid pattern
step = 100
for y in range(0, min(500, img_array.shape[0]), step):
    row_values = []
    for x in range(0, min(1000, img_array.shape[1]), step):
        pixel = img_array[y, x]
        # Take the brightest channel
        max_val = max(pixel[0], pixel[1], pixel[2])
        if 32 <= max_val < 127:  # ASCII range
            row_values.append(chr(max_val))
        else:
            row_values.append('.')
    
    text = ''.join(row_values)
    if text.strip('.'):
        print(f"    Row {y}: {text}")

print("\n" + "="*60)
print("Check the binary_*.jpg files - they should show text clearly!")
print("="*60)
