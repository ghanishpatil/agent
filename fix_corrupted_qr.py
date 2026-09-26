#!/usr/bin/env python3
"""
Fix and decode corrupted QR code
"""
import cv2
import numpy as np
from PIL import Image

print("="*80)
print("CORRUPTED QR CODE REPAIR AND DECODER")
print("="*80)

img_path = "Corrupted_QR.png"

# Load the image
img = cv2.imread(img_path)
if img is None:
    print(f"✗ Could not load {img_path}")
    exit(1)

print(f"\n[Image Info]")
print(f"  Size: {img.shape[1]}x{img.shape[0]}")
print(f"  Channels: {img.shape[2] if len(img.shape) > 2 else 1}")

# Method 1: Direct decode attempt
print("\n[Method 1: Direct decode]")
detector = cv2.QRCodeDetector()
data, bbox, straight_qrcode = detector.detectAndDecode(img)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Failed")

# Method 2: Convert to grayscale and threshold
print("\n[Method 2: Grayscale + Threshold]")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
data, bbox, straight_qrcode = detector.detectAndDecode(thresh)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Failed")

# Method 3: Adaptive threshold
print("\n[Method 3: Adaptive Threshold]")
adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY, 11, 2)
data, bbox, straight_qrcode = detector.detectAndDecode(adaptive)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Failed")

# Method 4: Otsu's thresholding
print("\n[Method 4: Otsu's Threshold]")
_, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
data, bbox, straight_qrcode = detector.detectAndDecode(otsu)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Failed")

# Method 5: Morphological operations to fix corruption
print("\n[Method 5: Morphological Repair]")
kernel = np.ones((3,3), np.uint8)
# Close small holes
closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
data, bbox, straight_qrcode = detector.detectAndDecode(closed)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Failed")

# Method 6: Denoise + threshold
print("\n[Method 6: Denoise]")
denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
_, thresh_denoised = cv2.threshold(denoised, 127, 255, cv2.THRESH_BINARY)
data, bbox, straight_qrcode = detector.detectAndDecode(thresh_denoised)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Failed")

# Method 7: Invert colors
print("\n[Method 7: Inverted]")
inverted = cv2.bitwise_not(thresh)
data, bbox, straight_qrcode = detector.detectAndDecode(inverted)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Failed")

# Method 8: Try pyzbar
print("\n[Method 8: pyzbar library]")
try:
    from pyzbar.pyzbar import decode
    pil_img = Image.open(img_path)
    decoded_objects = decode(pil_img)
    if decoded_objects:
        for obj in decoded_objects:
            print(f"  ✓ SUCCESS: {obj.data.decode('utf-8')}")
    else:
        print("  ✗ Failed")
except ImportError:
    print("  ⚠ pyzbar not installed")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Method 9: Multiple threshold values
print("\n[Method 9: Multiple thresholds]")
for thresh_val in [50, 75, 100, 127, 150, 175, 200]:
    _, thresh_test = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
    data, bbox, straight_qrcode = detector.detectAndDecode(thresh_test)
    if data:
        print(f"  ✓ SUCCESS at threshold {thresh_val}: {data}")
        break
else:
    print("  ✗ Failed at all thresholds")

# Method 10: Resize and try
print("\n[Method 10: Resize attempts]")
for scale in [0.5, 1.5, 2.0, 3.0]:
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)
    data, bbox, straight_qrcode = detector.detectAndDecode(resized)
    if data:
        print(f"  ✓ SUCCESS at scale {scale}: {data}")
        break
else:
    print("  ✗ Failed at all scales")

# Method 11: Bilateral filter (edge-preserving smoothing)
print("\n[Method 11: Bilateral Filter]")
bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
_, thresh_bilateral = cv2.threshold(bilateral, 127, 255, cv2.THRESH_BINARY)
data, bbox, straight_qrcode = detector.detectAndDecode(thresh_bilateral)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Failed")

# Method 12: Median blur
print("\n[Method 12: Median Blur]")
median = cv2.medianBlur(gray, 5)
_, thresh_median = cv2.threshold(median, 127, 255, cv2.THRESH_BINARY)
data, bbox, straight_qrcode = detector.detectAndDecode(thresh_median)
if data:
    print(f"  ✓ SUCCESS: {data}")
else:
    print("  ✗ Failed")

# Save processed versions for manual inspection
print("\n[Saving processed images for inspection]")
cv2.imwrite("qr_grayscale.png", gray)
cv2.imwrite("qr_threshold.png", thresh)
cv2.imwrite("qr_adaptive.png", adaptive)
cv2.imwrite("qr_otsu.png", otsu)
cv2.imwrite("qr_morphed.png", closed)
print("  ✓ Saved: qr_grayscale.png, qr_threshold.png, qr_adaptive.png, qr_otsu.png, qr_morphed.png")

print("\n" + "="*80)
print("If all methods failed, the QR code may be too corrupted.")
print("Check the saved images to see which preprocessing looks best.")
print("="*80)
