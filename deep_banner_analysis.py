#!/usr/bin/env python3
"""
Deep analysis of the banner image
"""

from PIL import Image
import numpy as np

img = Image.open('lore_banner.png')
pixels = np.array(img)

print("="*60)
print("DEEP BANNER ANALYSIS")
print("="*60)

print(f"\nImage size: {img.size}")
print(f"Mode: {img.mode}")
print(f"Array shape: {pixels.shape}")

# Extract all LSBs from all channels
print("\n[*] Extracting LSBs from all channels...")
lsb_r = pixels[:, :, 0] & 1
lsb_g = pixels[:, :, 1] & 1
lsb_b = pixels[:, :, 2] & 1

# Flatten and convert to binary string
flat_r = lsb_r.flatten()
flat_g = lsb_g.flatten()
flat_b = lsb_b.flatten()

# Try different channel combinations
print("\n[*] Trying different channel combinations...")

for name, data in [('Red', flat_r), ('Green', flat_g), ('Blue', flat_b)]:
    binary_str = ''.join(str(b) for b in data[:8000])
    
    # Convert to ASCII
    text = ''
    for i in range(0, min(len(binary_str), 8000), 8):
        byte = binary_str[i:i+8]
        if len(byte) == 8:
            val = int(byte, 2)
            if 32 <= val <= 126:
                text += chr(val)
            elif val == 0:
                break
            else:
                text += '.'
    
    print(f"\n{name} channel LSB:")
    print(f"  First 100 chars: {text[:100]}")
    if 'Kaal{' in text or 'kaal{' in text.lower():
        print(f"  [!] FLAG FOUND: {text}")

# Try interleaved
print("\n[*] Trying interleaved RGB...")
interleaved = []
for i in range(min(len(flat_r), len(flat_g), len(flat_b))):
    interleaved.extend([flat_r[i], flat_g[i], flat_b[i]])

binary_str = ''.join(str(b) for b in interleaved[:24000])
text = ''
for i in range(0, min(len(binary_str), 24000), 8):
    byte = binary_str[i:i+8]
    if len(byte) == 8:
        val = int(byte, 2)
        if 32 <= val <= 126:
            text += chr(val)
        elif val == 0:
            break
        else:
            text += '.'

print(f"  First 100 chars: {text[:100]}")
if 'Kaal{' in text or 'kaal{' in text.lower():
    print(f"  [!] FLAG FOUND: {text}")

# Check for patterns in pixel values
print("\n[*] Analyzing pixel value patterns...")
unique_r = np.unique(pixels[:, :, 0])
unique_g = np.unique(pixels[:, :, 1])
unique_b = np.unique(pixels[:, :, 2])

print(f"  Unique R values: {len(unique_r)}")
print(f"  Unique G values: {len(unique_g)}")
print(f"  Unique B values: {len(unique_b)}")

# Look for ASCII-range values
ascii_pixels = []
for y in range(pixels.shape[0]):
    for x in range(pixels.shape[1]):
        r, g, b = pixels[y, x, :3]
        if 32 <= r <= 126:
            ascii_pixels.append(('R', x, y, r, chr(r)))
        if 32 <= g <= 126:
            ascii_pixels.append(('G', x, y, g, chr(g)))
        if 32 <= b <= 126:
            ascii_pixels.append(('B', x, y, b, chr(b)))

if ascii_pixels:
    print(f"\n[*] Found {len(ascii_pixels)} ASCII-range pixel values")
    print(f"  First 50: {''.join([p[4] for p in ascii_pixels[:50]])}")
    
    # Try to extract text
    text = ''.join([p[4] for p in ascii_pixels])
    if 'Kaal{' in text or 'kaal{' in text.lower():
        print(f"  [!] FLAG FOUND: {text}")

print("\n" + "="*60)
