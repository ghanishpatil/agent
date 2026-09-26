#!/usr/bin/env python3
"""
Decode QR code from image
"""
from PIL import Image
import cv2
import numpy as np

print("="*80)
print("QR CODE DECODER")
print("="*80)

# Try multiple methods to decode the QR code

# Method 1: Using cv2 QRCodeDetector
print("\n[Method 1: OpenCV QRCodeDetector]")
try:
    # Load the image
    img = cv2.imread('qr_code.png')
    
    if img is None:
        print("  ✗ Could not load image")
    else:
        detector = cv2.QRCodeDetector()
        data, bbox, straight_qrcode = detector.detectAndDecode(img)
        
        if data:
            print(f"  ✓ Decoded: {data}")
        else:
            print("  ✗ No QR code detected")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Method 2: Using pyzbar
print("\n[Method 2: pyzbar]")
try:
    from pyzbar.pyzbar import decode
    from PIL import Image
    
    img = Image.open('qr_code.png')
    decoded_objects = decode(img)
    
    if decoded_objects:
        for obj in decoded_objects:
            print(f"  ✓ Type: {obj.type}")
            print(f"  ✓ Data: {obj.data.decode('utf-8')}")
    else:
        print("  ✗ No QR code detected")
except ImportError:
    print("  ✗ pyzbar not installed (pip install pyzbar)")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Method 3: Try preprocessing the image
print("\n[Method 3: With image preprocessing]")
try:
    img = cv2.imread('qr_code.png')
    
    if img is not None:
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        detector = cv2.QRCodeDetector()
        data, bbox, straight_qrcode = detector.detectAndDecode(thresh)
        
        if data:
            print(f"  ✓ Decoded: {data}")
        else:
            print("  ✗ No QR code detected")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Method 4: Try with different scales
print("\n[Method 4: Multiple scales]")
try:
    img = cv2.imread('qr_code.png')
    
    if img is not None:
        for scale in [0.5, 1.0, 1.5, 2.0]:
            width = int(img.shape[1] * scale)
            height = int(img.shape[0] * scale)
            resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
            
            detector = cv2.QRCodeDetector()
            data, bbox, straight_qrcode = detector.detectAndDecode(resized)
            
            if data:
                print(f"  ✓ Scale {scale}: {data}")
                break
        else:
            print("  ✗ No QR code detected at any scale")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "="*80)
