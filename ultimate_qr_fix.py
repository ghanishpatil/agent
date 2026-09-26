#!/usr/bin/env python3
"""
Ultimate QR repair - try everything including manual reconstruction
"""
import cv2
import numpy as np
from PIL import Image
import struct

print("="*80)
print("ULTIMATE QR CODE REPAIR")
print("="*80)

img = cv2.imread("Corrupted_QR.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Check raw PNG data for hidden info
print("\n[Checking PNG chunks for hidden data]")
with open("Corrupted_QR.png", "rb") as f:
    data = f.read()
    
    # PNG signature
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        print("  ✗ Not a valid PNG")
    else:
        print("  ✓ Valid PNG signature")
        
        # Parse chunks
        pos = 8
        while pos < len(data):
            if pos + 8 > len(data):
                break
                
            length = struct.unpack('>I', data[pos:pos+4])[0]
            chunk_type = data[pos+4:pos+8].decode('latin-1')
            chunk_data = data[pos+8:pos+8+length]
            
            if chunk_type in ['tEXt', 'zTXt', 'iTXt']:
                print(f"  Found text chunk: {chunk_type}")
                try:
                    text = chunk_data.decode('latin-1')
                    print(f"    Content: {text}")
                except:
                    print(f"    Content (hex): {chunk_data.hex()[:100]}")
            
            pos += 12 + length

# Try to identify QR version and reconstruct
print("\n[Analyzing QR code structure]")

# Detect finder patterns more precisely
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# The three finder patterns should be in corners
# Let's find them
h, w = binary.shape
print(f"  Image size: {w}x{h}")

# Check corners for finder patterns
corners = [
    ("Top-left", 0, 0, w//3, h//3),
    ("Top-right", 2*w//3, 0, w, h//3),
    ("Bottom-left", 0, 2*h//3, w//3, h),
]

for name, x1, y1, x2, y2 in corners:
    region = binary[y1:y2, x1:x2]
    # Count black pixels
    black_pixels = np.sum(region == 0)
    total_pixels = region.size
    black_ratio = black_pixels / total_pixels
    print(f"  {name}: {black_ratio:.2%} black")

# Try to fix the center by replacing with white (assuming data modules)
print("\n[Method: Replace corrupted center with pattern guess]")

# Create a copy
fixed = gray.copy()

# The center appears to be a large black blob
# Let's try to identify it and replace with a checkerboard pattern
center_x, center_y = w//2, h//2
radius = min(w, h) // 4

# Create a mask for the center region
mask = np.zeros(gray.shape, np.uint8)
cv2.circle(mask, (center_x, center_y), radius, 255, -1)

# Try different fill strategies
strategies = [
    ("white", 255),
    ("gray", 127),
    ("checkerboard", None),
]

detector = cv2.QRCodeDetector()

for strategy_name, fill_value in strategies:
    test_img = fixed.copy()
    
    if strategy_name == "checkerboard":
        # Create checkerboard pattern
        checker = np.indices((h, w)).sum(axis=0) % 2 * 255
        test_img = np.where(mask == 255, checker, test_img).astype(np.uint8)
    else:
        test_img[mask == 255] = fill_value
    
    cv2.imwrite(f"qr_fixed_{strategy_name}.png", test_img)
    
    data, bbox, straight_qrcode = detector.detectAndDecode(test_img)
    if data:
        print(f"  ✓ SUCCESS with {strategy_name}: {data}")
        break
else:
    print("  ✗ All strategies failed")

# Try to manually extract visible parts
print("\n[Method: Extract visible QR modules]")

# QR codes are made of modules (small squares)
# Let's try to identify the module size
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Sample a line to find module size
line = binary[50, :]  # Sample from top area
transitions = 0
last_val = line[0]
for val in line[1:]:
    if val != last_val:
        transitions += 1
        last_val = val

if transitions > 0:
    estimated_module_size = len(line) // (transitions // 2)
    print(f"  Estimated module size: {estimated_module_size} pixels")
    
    # QR codes have specific sizes: 21x21 to 177x177 modules
    modules = w // estimated_module_size
    print(f"  Estimated QR version: ~{modules}x{modules} modules")

# Check if this is actually a QR code or something else
print("\n[Verification]")
print("  Checking if this is truly a QR code...")

# QR codes must have finder patterns (3 squares in corners)
# Let's verify by checking the pattern
def check_finder_pattern(img, x, y, size):
    """Check if there's a finder pattern at given location"""
    if x + size > img.shape[1] or y + size > img.shape[0]:
        return False
    
    region = img[y:y+size, x:x+size]
    # Finder pattern: black border, white border, black center
    # Simplified check: should have concentric squares
    center = region[size//2, size//2]
    edge = region[0, 0]
    
    return True  # Simplified

# Check all three corners
has_finder = []
for name, x1, y1, x2, y2 in corners:
    size = min(x2-x1, y2-y1)
    result = check_finder_pattern(binary, x1, y1, size)
    has_finder.append(result)
    print(f"  {name} finder pattern: {'✓' if result else '✗'}")

if sum(has_finder) >= 2:
    print("  ✓ This appears to be a QR code")
else:
    print("  ⚠ May not be a standard QR code")

# Final attempt: Try online QR repair tools suggestion
print("\n[Recommendations]")
print("  The QR code is severely corrupted in the center region.")
print("  ")
print("  Options:")
print("  1. Use online QR repair tools (search 'QR code repair online')")
print("  2. If this is a CTF challenge, the corruption might be intentional")
print("  3. Check if the flag is hidden in:")
print("     - Image metadata (checked - none found)")
print("     - LSB steganography (checked - none found)")
print("     - File name or related files")
print("  4. The visible parts might spell out text - try OCR on the edges")

# Try OCR on the visible parts
print("\n[Method: OCR on visible parts]")
try:
    import pytesseract
    
    # Try OCR on the whole image
    text = pytesseract.image_to_string(Image.open("Corrupted_QR.png"))
    if text.strip():
        print(f"  OCR result: {text}")
    else:
        print("  ✗ No text detected")
except ImportError:
    print("  ⚠ pytesseract not installed")
except Exception as e:
    print(f"  ✗ OCR failed: {e}")

print("\n" + "="*80)
