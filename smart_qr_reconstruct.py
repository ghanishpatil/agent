#!/usr/bin/env python3
"""
Smart QR reconstruction using error correction and brute force
"""
import cv2
import numpy as np
import itertools

print("="*80)
print("SMART QR CODE RECONSTRUCTION")
print("="*80)

img = cv2.imread("Corrupted_QR.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

detector = cv2.QRCodeDetector()

# The QR has finder patterns, so structure is intact
# The center corruption is the issue
# Let's try to systematically replace the corrupted area

print("\n[Strategy: Systematic center replacement]")

h, w = binary.shape
center_x, center_y = w//2, h//2

# Try different corruption removal strategies
print("  Trying different center fill patterns...")

# Strategy 1: Remove the large black blob by making it white
test1 = binary.copy()
# Find large black regions
_, inv = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)
contours, _ = cv2.findContours(inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 50000:  # Large blob
        cv2.drawContours(test1, [cnt], -1, 255, -1)
        print(f"    Removed blob of area {area}")

cv2.imwrite("qr_blob_removed.png", test1)
data, bbox, straight_qrcode = detector.detectAndDecode(test1)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Blob removal failed")

# Strategy 2: Erode the black regions
print("\n  Trying erosion...")
kernel = np.ones((5,5), np.uint8)
eroded = cv2.erode(binary, kernel, iterations=2)
cv2.imwrite("qr_eroded.png", eroded)
data, bbox, straight_qrcode = detector.detectAndDecode(eroded)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Erosion failed")

# Strategy 3: Opening (erosion followed by dilation)
print("\n  Trying morphological opening...")
opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
cv2.imwrite("qr_opened.png", opened)
data, bbox, straight_qrcode = detector.detectAndDecode(opened)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Opening failed")

# Strategy 4: Try to detect and remove only the anomalous black region
print("\n  Trying smart blob detection...")
test4 = binary.copy()

# Calculate expected module size from finder patterns
# Finder patterns are 7x7 modules
# Let's measure the top-left finder pattern
tl_region = binary[0:h//3, 0:w//3]
# Find the outer black square
contours, _ = cv2.findContours(255-tl_region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if contours:
    largest = max(contours, key=cv2.contourArea)
    x, y, fw, fh = cv2.boundingRect(largest)
    module_size = fw // 7  # Finder pattern is 7 modules
    print(f"    Detected module size: {module_size} pixels")
    
    # Now identify blobs that are too large to be valid QR modules
    inv = 255 - binary
    contours, _ = cv2.findContours(inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        expected_max_area = (module_size * 10) ** 2  # Max 10x10 modules
        if area > expected_max_area:
            print(f"    Removing anomalous blob: {area} pixels")
            cv2.drawContours(test4, [cnt], -1, 255, -1)
    
    cv2.imwrite("qr_smart_cleaned.png", test4)
    data, bbox, straight_qrcode = detector.detectAndDecode(test4)
    if data:
        print(f"  ✓ SUCCESS: {data}")
    else:
        print("  ✗ Smart cleaning failed")

# Strategy 5: Try to use only the edges (remove center completely)
print("\n  Trying edge-only decode...")
test5 = binary.copy()
# Mask out the center
cv2.circle(test5, (center_x, center_y), min(w,h)//3, 255, -1)
cv2.imwrite("qr_center_removed.png", test5)
data, bbox, straight_qrcode = detector.detectAndDecode(test5)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Center removal failed")

# Strategy 6: Try different kernel sizes for morphological operations
print("\n  Trying various kernel sizes...")
for ksize in [3, 7, 9, 11]:
    kernel = np.ones((ksize, ksize), np.uint8)
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    data, bbox, straight_qrcode = detector.detectAndDecode(opened)
    if data:
        print(f"  ✓ SUCCESS with kernel {ksize}: {data}")
        break
else:
    print("  ✗ All kernel sizes failed")

# Strategy 7: Combine multiple techniques
print("\n  Trying combined approach...")
# First remove large blobs
test7 = binary.copy()
inv = 255 - binary
contours, _ = cv2.findContours(inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 30000:
        cv2.drawContours(test7, [cnt], -1, 255, -1)

# Then apply opening
kernel = np.ones((3,3), np.uint8)
test7 = cv2.morphologyEx(test7, cv2.MORPH_OPEN, kernel)

# Then apply closing
test7 = cv2.morphologyEx(test7, cv2.MORPH_CLOSE, kernel)

cv2.imwrite("qr_combined.png", test7)
data, bbox, straight_qrcode = detector.detectAndDecode(test7)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Combined approach failed")

# Strategy 8: Try on the inverted image
print("\n  Trying inverted image...")
inverted = 255 - binary
data, bbox, straight_qrcode = detector.detectAndDecode(inverted)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Inversion failed")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("The QR code has a large black corruption in the center.")
print("All standard repair techniques have been attempted.")
print("")
print("Next steps:")
print("1. Check the processed images (qr_*.png) manually")
print("2. Try online QR repair tools")
print("3. If this is a CTF, the corruption might encode the flag itself")
print("4. Check if there are other files or hints related to this challenge")
print("="*80)
