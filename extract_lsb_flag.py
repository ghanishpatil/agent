from PIL import Image
import numpy as np

image_path = r"D:\mission-git-hackss\board.png"

print("="*80)
print("LSB EXTRACTION - LOOKING FOR FLAG")
print("="*80)

img = Image.open(image_path)

# Try different channel combinations
channels_to_try = [
    ('RGB', img.convert('RGB')),
    ('RGBA', img if img.mode == 'RGBA' else None),
]

for mode, img_data in channels_to_try:
    if img_data is None:
        continue
    
    print(f"\n[Extracting from {mode}]")
    pixels = np.array(img_data)
    
    # Try each channel
    channel_names = ['R', 'G', 'B', 'A'][:pixels.shape[2]]
    
    for ch_idx, ch_name in enumerate(channel_names):
        print(f"\n  Channel {ch_name}:")
        
        # Extract LSB
        lsb = pixels[:, :, ch_idx] & 1
        lsb_flat = lsb.flatten()
        
        # Convert to bytes
        byte_array = []
        for i in range(len(lsb_flat) // 8):
            byte_val = 0
            for bit in range(8):
                byte_val = (byte_val << 1) | lsb_flat[i*8 + bit]
            byte_array.append(byte_val)
        
        # Convert to bytes object
        data = bytes(byte_array)
        
        # Look for flag patterns
        if b'KAAL{' in data:
            idx = data.index(b'KAAL{')
            flag_end = data.find(b'}', idx)
            if flag_end != -1:
                flag = data[idx:flag_end+1].decode('ascii', errors='ignore')
                print(f"    FOUND FLAG: {flag}")
        
        if b'FLAG{' in data:
            idx = data.index(b'FLAG{')
            flag_end = data.find(b'}', idx)
            if flag_end != -1:
                flag = data[idx:flag_end+1].decode('ascii', errors='ignore')
                print(f"    FOUND FLAG: {flag}")
        
        # Check first 500 bytes for any readable text
        preview = data[:500]
        printable = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in preview])
        if 'KAAL' in printable or 'FLAG' in printable or 'flag' in printable:
            print(f"    Preview: {printable}")
        
        # Try reverse bit order
        byte_array_rev = []
        for i in range(len(lsb_flat) // 8):
            byte_val = 0
            for bit in range(8):
                byte_val = (byte_val << 1) | lsb_flat[i*8 + (7-bit)]
            byte_array_rev.append(byte_val)
        
        data_rev = bytes(byte_array_rev)
        if b'KAAL{' in data_rev:
            idx = data_rev.index(b'KAAL{')
            flag_end = data_rev.find(b'}', idx)
            if flag_end != -1:
                flag = data_rev[idx:flag_end+1].decode('ascii', errors='ignore')
                print(f"    FOUND FLAG (reversed bits): {flag}")

# Try combining channels
print("\n[Trying channel combinations]")
img_rgb = img.convert('RGB')
pixels = np.array(img_rgb)

# Try R+G+B interleaved
print("\n  R+G+B interleaved:")
combined_bits = []
for y in range(pixels.shape[0]):
    for x in range(pixels.shape[1]):
        combined_bits.append(pixels[y, x, 0] & 1)  # R
        combined_bits.append(pixels[y, x, 1] & 1)  # G
        combined_bits.append(pixels[y, x, 2] & 1)  # B

byte_array = []
for i in range(len(combined_bits) // 8):
    byte_val = 0
    for bit in range(8):
        byte_val = (byte_val << 1) | combined_bits[i*8 + bit]
    byte_array.append(byte_val)

data = bytes(byte_array)
if b'KAAL{' in data:
    idx = data.index(b'KAAL{')
    flag_end = data.find(b'}', idx)
    if flag_end != -1:
        flag = data[idx:flag_end+1].decode('ascii', errors='ignore')
        print(f"    FOUND FLAG: {flag}")

# Check for common steganography tools signatures
print("\n[Checking for steganography tool signatures]")
with open(image_path, 'rb') as f:
    raw_data = f.read()
    
    # Look for common markers
    if b'steghide' in raw_data.lower():
        print("  Steghide signature found!")
    if b'outguess' in raw_data.lower():
        print("  Outguess signature found!")
    if b'openstego' in raw_data.lower():
        print("  OpenStego signature found!")
    
    # Look for KAAL in raw data
    if b'KAAL{' in raw_data:
        idx = raw_data.index(b'KAAL{')
        flag_end = raw_data.find(b'}', idx)
        if flag_end != -1:
            flag = raw_data[idx:flag_end+1].decode('ascii', errors='ignore')
            print(f"  FOUND FLAG IN RAW DATA: {flag}")

print("\n" + "="*80)
