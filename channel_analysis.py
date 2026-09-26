#!/usr/bin/env python3
"""
Analyze individual color channels for hidden data
"""
from PIL import Image
import numpy as np
import re

image_path = "image_sJM6Gg8.jpg"

print("="*60)
print("COLOR CHANNEL ANALYSIS")
print("="*60)

img = Image.open(image_path)
img_array = np.array(img)

print(f"\nImage shape: {img_array.shape}")

# Split into R, G, B channels
r_channel = img_array[:,:,0]
g_channel = img_array[:,:,1]
b_channel = img_array[:,:,2]

# Check LSB of each channel separately
print("\n[1] LSB extraction from each channel:")

for channel_name, channel in [('Red', r_channel), ('Green', g_channel), ('Blue', b_channel)]:
    print(f"\n    {channel_name} channel:")
    
    # Extract LSB
    lsb_bits = (channel & 1).flatten()
    
    # Convert to bytes
    lsb_bytes = []
    for i in range(0, min(len(lsb_bits), 10000), 8):
        if i + 8 <= len(lsb_bits):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | lsb_bits[i + j]
            lsb_bytes.append(byte)
    
    # Try to decode as text
    lsb_text = bytes(lsb_bytes).decode('ascii', errors='ignore')
    print(f"        First 200 chars: {lsb_text[:200]}")
    
    if 'Kaal{' in lsb_text:
        flag = re.search(r'Kaal\{[^}]+\}', lsb_text)
        if flag:
            print(f"\n[+] FLAG FOUND IN {channel_name} CHANNEL: {flag.group(0)}")

# Check for patterns in pixel values
print("\n[2] Statistical analysis:")
print(f"    Red channel - Mean: {r_channel.mean():.2f}, Std: {r_channel.std():.2f}")
print(f"    Green channel - Mean: {g_channel.mean():.2f}, Std: {g_channel.std():.2f}")
print(f"    Blue channel - Mean: {b_channel.mean():.2f}, Std: {b_channel.std():.2f}")

# Check if there's a specific pattern in one channel
print("\n[3] Checking for unusual patterns:")

# Look for pixels where one channel is significantly different
unusual_pixels = []
for i in range(min(100, img_array.shape[0])):
    for j in range(min(100, img_array.shape[1])):
        r, g, b = img_array[i, j]
        # Check if one channel is very different from others
        if abs(r - g) > 200 or abs(r - b) > 200 or abs(g - b) > 200:
            unusual_pixels.append((i, j, r, g, b))

if unusual_pixels:
    print(f"    Found {len(unusual_pixels)} unusual pixels")
    for pixel in unusual_pixels[:10]:
        print(f"        Position ({pixel[0]}, {pixel[1]}): R={pixel[2]}, G={pixel[3]}, B={pixel[4]}")

# Try extracting data from specific bit planes
print("\n[4] Checking different bit planes:")
for bit_plane in [0, 1, 2]:  # LSB, 2nd LSB, 3rd LSB
    print(f"\n    Bit plane {bit_plane}:")
    
    # Extract from red channel
    bits = ((r_channel >> bit_plane) & 1).flatten()
    
    # Convert to bytes
    bytes_data = []
    for i in range(0, min(len(bits), 1000), 8):
        if i + 8 <= len(bits):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            bytes_data.append(byte)
    
    text = bytes(bytes_data).decode('ascii', errors='ignore')
    if 'Kaal' in text or 'flag' in text.lower():
        print(f"        Found interesting text: {text[:200]}")
        if 'Kaal{' in text:
            flag = re.search(r'Kaal\{[^}]+\}', text)
            if flag:
                print(f"\n[+] FLAG FOUND: {flag.group(0)}")

print("\n" + "="*60)
