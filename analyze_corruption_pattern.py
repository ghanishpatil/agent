#!/usr/bin/env python3
"""
Analyze the corruption pattern - maybe it encodes the flag
"""
import cv2
import numpy as np
from PIL import Image

print("="*80)
print("CORRUPTION PATTERN ANALYSIS")
print("="*80)

img = cv2.imread("Corrupted_QR.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Extract the corrupted region
print("\n[Extracting corruption pattern]")
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

# Find the large black blob
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
largest_blob = max(contours, key=cv2.contourArea)

# Get bounding box
x, y, w, h = cv2.boundingRect(largest_blob)
print(f"  Corruption region: {x},{y} size {w}x{h}")

# Extract just the corruption
corruption = binary[y:y+h, x:x+w]
cv2.imwrite("corruption_pattern.png", corruption)

# Check if the corruption itself forms text or a pattern
print("\n[Analyzing corruption shape]")
print(f"  Area: {cv2.contourArea(largest_blob)}")
print(f"  Perimeter: {cv2.arcLength(largest_blob, True)}")

# Try to see if it spells something
print("\n[Checking if corruption forms letters/numbers]")

# Save the corruption as a separate image for inspection
corruption_img = np.zeros_like(gray)
cv2.drawContours(corruption_img, [largest_blob], -1, 255, -1)
cv2.imwrite("corruption_only.png", corruption_img)

# Try OCR on the corruption
try:
    import pytesseract
    text = pytesseract.image_to_string(corruption_img)
    if text.strip():
        print(f"  OCR result: {text}")
    else:
        print("  ✗ No text detected in corruption")
except:
    print("  ⚠ OCR not available")

# Check if the corruption has a specific shape
print("\n[Shape analysis]")
# Approximate the contour
epsilon = 0.01 * cv2.arcLength(largest_blob, True)
approx = cv2.approxPolyDP(largest_blob, epsilon, True)
print(f"  Approximated to {len(approx)} points")

# Check if it's a recognizable shape
if len(approx) == 3:
    print("  Shape: Triangle")
elif len(approx) == 4:
    print("  Shape: Quadrilateral")
elif len(approx) > 10:
    print("  Shape: Complex/Irregular")

# Maybe the answer is to look at what's NOT corrupted
print("\n[Analyzing non-corrupted regions]")

# Get the QR code without the corruption
clean_attempt = gray.copy()
cv2.drawContours(clean_attempt, [largest_blob], -1, 255, -1)
cv2.imwrite("qr_corruption_filled_white.png", clean_attempt)

# Try to decode
detector = cv2.QRCodeDetector()
data, bbox, straight_qrcode = detector.detectAndDecode(clean_attempt)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Still can't decode")

# Check the actual pixel values in the corruption
print("\n[Corruption pixel analysis]")
corruption_pixels = img[binary == 255]
if len(corruption_pixels) > 0:
    print(f"  Corruption pixels: {len(corruption_pixels)}")
    print(f"  Mean color: {corruption_pixels.mean(axis=0)}")
    print(f"  Std dev: {corruption_pixels.std(axis=0)}")
    
    # Check if there's variation (hidden data)
    if corruption_pixels.std() > 5:
        print("  ⚠ Variation detected - might contain hidden data!")
        
        # Extract and visualize the variation
        corruption_detail = img.copy()
        mask = binary == 0
        corruption_detail[mask] = 255
        cv2.imwrite("corruption_detail.png", corruption_detail)
        print("  Saved corruption_detail.png")

# Try reading the QR code data manually from the visible parts
print("\n[Manual QR reading attempt]")
print("  The QR code has 3 finder patterns visible.")
print("  Module size: ~42 pixels")
print("  This suggests a small QR code (probably version 1-3)")
print("  ")
print("  For a version 1 QR code (21x21 modules):")
print("  - Can store up to 25 alphanumeric characters")
print("  - Has error correction (L/M/Q/H levels)")
print("  ")
print("  The corruption covers the data area, but QR codes have")
print("  error correction. However, this corruption is too extensive.")

# Final check: Is there text hidden in the filename or nearby?
print("\n[Checking for related clues]")
print("  Filename: Corrupted_QR.png")
print("  This suggests the corruption is intentional.")
print("  ")
print("  Possible solutions:")
print("  1. The flag might be in the corruption pattern itself")
print("  2. There might be other files that help decode this")
print("  3. The corruption might need to be XORed or combined with something")
print("  4. Check if there's a 'key' image or file nearby")

print("\n" + "="*80)
