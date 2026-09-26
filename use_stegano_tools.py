from stegano import lsb, exifHeader
from PIL import Image
import numpy as np

print("="*80)
print("STEGANO TOOLS ANALYSIS")
print("="*80)

image_path = "board.png"

# 1. LSB extraction
print("\n[1. LSB EXTRACTION]")
try:
    secret = lsb.reveal(image_path)
    if secret:
        print(f"LSB revealed: {secret}")
        if 'KAAL' in secret or 'FLAG' in secret:
            print("*** FLAG FOUND ***")
    else:
        print("No LSB data found")
except Exception as e:
    print(f"LSB extraction failed: {e}")

# 2. EXIF Header
print("\n[2. EXIF HEADER EXTRACTION]")
try:
    secret = exifHeader.reveal(image_path)
    if secret:
        print(f"EXIF revealed: {secret}")
        if 'KAAL' in secret or 'FLAG' in secret:
            print("*** FLAG FOUND ***")
    else:
        print("No EXIF hidden data found")
except Exception as e:
    print(f"EXIF extraction failed: {e}")

# 3. Check interesting bit planes manually
print("\n[3. ANALYZING INTERESTING BIT PLANES]")
interesting_planes = [
    ('R', 1), ('R', 3), ('R', 4), ('R', 7),
    ('G', 0), ('G', 3), ('G', 4), ('G', 5), ('G', 6),
    ('B', 1), ('B', 7)
]

img = Image.open(image_path)
img_array = np.array(img)

for channel_name, bit in interesting_planes:
    channel_idx = {'R': 0, 'G': 1, 'B': 2, 'A': 3}[channel_name]
    
    # Extract bit plane
    bit_plane = (img_array[:, :, channel_idx] >> bit) & 1
    
    # Try to read as text
    bit_flat = bit_plane.flatten()
    
    # Convert to bytes
    byte_array = []
    for i in range(len(bit_flat) // 8):
        byte_val = 0
        for b in range(8):
            byte_val = (byte_val << 1) | bit_flat[i*8 + b]
        byte_array.append(byte_val)
    
    data = bytes(byte_array)
    
    # Check for flag
    if b'KAAL{' in data:
        idx = data.index(b'KAAL{')
        end_idx = data.find(b'}', idx)
        if end_idx != -1:
            flag = data[idx:end_idx+1].decode('ascii', errors='ignore')
            print(f"\n*** FLAG FOUND in {channel_name} bit {bit}: {flag} ***")
    
    # Check for readable text
    text = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in byte_array[:200]])
    if text.count('.') < len(text) * 0.7:  # Less than 70% dots = might be text
        print(f"\n{channel_name} bit {bit} preview: {text[:100]}")

# 4. Try different LSB combinations
print("\n[4. TRYING DIFFERENT LSB PATTERNS]")

# Try reading from specific bit planes
for channel_idx, channel_name in enumerate(['R', 'G', 'B']):
    for bit_pos in range(3):  # Try bits 0, 1, 2
        bit_plane = (img_array[:, :, channel_idx] >> bit_pos) & 1
        bit_flat = bit_plane.flatten()
        
        byte_array = []
        for i in range(min(10000, len(bit_flat) // 8)):
            byte_val = 0
            for b in range(8):
                byte_val = (byte_val << 1) | bit_flat[i*8 + b]
            byte_array.append(byte_val)
        
        data = bytes(byte_array)
        if b'KAAL{' in data:
            idx = data.index(b'KAAL{')
            end_idx = data.find(b'}', idx)
            if end_idx != -1:
                flag = data[idx:end_idx+1].decode('ascii', errors='ignore')
                print(f"\n*** FLAG FOUND in {channel_name} bit {bit_pos}: {flag} ***")

# 5. Check for patterns in bit plane images
print("\n[5. VISUAL INSPECTION OF BIT PLANES]")
print("Check these bit plane images for visual patterns:")
for channel_name, bit in interesting_planes:
    filename = f'bitplane_{channel_name}_{bit}.png'
    print(f"  {filename}")

print("\n" + "="*80)
