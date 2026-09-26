#!/usr/bin/env python3
"""
Advanced QR code repair - reconstruct missing parts
"""
import cv2
import numpy as np
from PIL import Image

print("="*80)
print("ADVANCED QR CODE RECONSTRUCTION")
print("="*80)

img = cv2.imread("Corrupted_QR.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

print("\n[Analyzing QR structure]")

# QR codes have finder patterns (the three squares in corners)
# Let's detect them
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Find contours
contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print(f"  Found {len(contours)} contours")

# Look for square-like contours (finder patterns)
finder_patterns = []
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 1000:  # Significant size
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        if len(approx) == 4:  # Square-ish
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h
            if 0.8 < aspect_ratio < 1.2:  # Nearly square
                finder_patterns.append((x, y, w, h))

print(f"  Found {len(finder_patterns)} potential finder patterns")

# Method: Try to reconstruct the center corrupted area
print("\n[Method: Inpainting corrupted region]")

# Create a mask for the corrupted area (the large black blob in center)
# Detect large black regions
_, inv_binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

# Find the large corrupted blob
kernel = np.ones((5,5), np.uint8)
dilated = cv2.dilate(inv_binary, kernel, iterations=2)

# Find contours of corrupted regions
contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Create mask for inpainting
mask = np.zeros(gray.shape, np.uint8)
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 10000:  # Large corrupted area
        cv2.drawContours(mask, [cnt], -1, 255, -1)

# Inpaint
inpainted = cv2.inpaint(gray, mask, 3, cv2.INPAINT_TELEA)
cv2.imwrite("qr_inpainted.png", inpainted)
print("  ✓ Saved inpainted version")

# Try to decode inpainted
detector = cv2.QRCodeDetector()
data, bbox, straight_qrcode = detector.detectAndDecode(inpainted)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Still can't decode")

# Method: Manual reconstruction based on QR structure
print("\n[Method: Pattern-based reconstruction]")

# QR codes have specific patterns - try to identify and fix them
# The center area seems to be the issue

# Try edge detection to see structure
edges = cv2.Canny(gray, 50, 150)
cv2.imwrite("qr_edges.png", edges)

# Method: Try to extract data from partial QR
print("\n[Method: Partial data extraction]")

# Even corrupted QR codes might have error correction
# Let's try different error correction levels with zbar
try:
    from pyzbar import pyzbar
    
    # Try on various processed versions
    versions = [
        ("original", img),
        ("grayscale", gray),
        ("binary", binary),
        ("inpainted", inpainted),
    ]
    
    for name, test_img in versions:
        decoded = pyzbar.decode(test_img)
        if decoded:
            print(f"  ✓ SUCCESS with {name}: {decoded[0].data.decode('utf-8')}")
            break
    else:
        print("  ✗ pyzbar couldn't decode any version")
        
except ImportError:
    print("  ⚠ pyzbar not available")

# Method: Try to manually read QR if we can see the pattern
print("\n[Method: Visual analysis]")
print("  The QR code appears to have a large black corruption in the center.")
print("  QR codes have error correction, but this may be too much damage.")
print("  ")
print("  Recommendations:")
print("  1. If you have the original source, try to get an uncorrupted version")
print("  2. The corruption appears intentional (CTF challenge?)")
print("  3. Check if there's metadata or alternate data in the image")

# Check image metadata
print("\n[Checking image metadata]")
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    
    pil_img = Image.open("Corrupted_QR.png")
    
    # Check for text chunks in PNG
    if hasattr(pil_img, 'text'):
        print("  PNG text chunks:")
        for key, value in pil_img.text.items():
            print(f"    {key}: {value}")
    
    # Check EXIF
    exif = pil_img.getexif()
    if exif:
        print("  EXIF data:")
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            print(f"    {tag}: {value}")
    
    if not hasattr(pil_img, 'text') and not exif:
        print("  No metadata found")
        
except Exception as e:
    print(f"  Error reading metadata: {e}")

# Try LSB steganography
print("\n[Checking for LSB steganography]")
# Extract LSB from each channel
for channel_idx, channel_name in enumerate(['B', 'G', 'R']):
    channel = img[:,:,channel_idx]
    lsb = (channel & 1) * 255
    cv2.imwrite(f"qr_lsb_{channel_name}.png", lsb)
    
    # Try to decode LSB version
    data, bbox, straight_qrcode = detector.detectAndDecode(lsb)
    if data:
        print(f"  ✓ SUCCESS in {channel_name} channel LSB: {data}")
        break
else:
    print("  ✗ No data in LSB")

print("\n" + "="*80)
