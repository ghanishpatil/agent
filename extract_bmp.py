#!/usr/bin/env python3
"""
Extract BMP file from flight_record.dat
"""

import struct

def find_and_extract_bmp(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Find BMP signature
    bmp_sig = b'BM'
    offset = data.find(bmp_sig)
    
    if offset == -1:
        print("No BMP signature found")
        return
    
    print(f"BMP signature found at offset: {offset}")
    
    # BMP header structure:
    # 0-1: "BM"
    # 2-5: File size (4 bytes, little endian)
    # 6-9: Reserved
    # 10-13: Offset to pixel data
    
    if offset + 14 > len(data):
        print("Not enough data for BMP header")
        return
    
    file_size = struct.unpack('<I', data[offset+2:offset+6])[0]
    pixel_offset = struct.unpack('<I', data[offset+10:offset+14])[0]
    
    print(f"BMP file size from header: {file_size} bytes")
    print(f"Pixel data offset: {pixel_offset}")
    
    # Extract the BMP
    if offset + file_size <= len(data):
        bmp_data = data[offset:offset+file_size]
        with open('extracted.bmp', 'wb') as f:
            f.write(bmp_data)
        print(f"Extracted BMP to extracted.bmp ({len(bmp_data)} bytes)")
    else:
        # Try to extract what we can
        bmp_data = data[offset:]
        with open('extracted.bmp', 'wb') as f:
            f.write(bmp_data)
        print(f"Extracted partial BMP to extracted.bmp ({len(bmp_data)} bytes)")
    
    # Also check if there are multiple BMPs
    print("\n=== Searching for all BMP signatures ===")
    search_offset = 0
    bmp_count = 0
    while True:
        idx = data.find(b'BM', search_offset)
        if idx == -1:
            break
        bmp_count += 1
        print(f"BMP #{bmp_count} at offset {idx}")
        
        if idx + 6 <= len(data):
            size = struct.unpack('<I', data[idx+2:idx+6])[0]
            print(f"  Size: {size} bytes")
        
        search_offset = idx + 1
    
    # Try to view the BMP info
    print("\n=== BMP Header Info ===")
    if len(bmp_data) >= 54:  # Minimum BMP header size
        print(f"Signature: {bmp_data[0:2]}")
        file_size = struct.unpack('<I', bmp_data[2:6])[0]
        reserved1 = struct.unpack('<H', bmp_data[6:8])[0]
        reserved2 = struct.unpack('<H', bmp_data[8:10])[0]
        offset_bits = struct.unpack('<I', bmp_data[10:14])[0]
        
        # DIB header
        dib_size = struct.unpack('<I', bmp_data[14:18])[0]
        width = struct.unpack('<i', bmp_data[18:22])[0]
        height = struct.unpack('<i', bmp_data[22:26])[0]
        planes = struct.unpack('<H', bmp_data[26:28])[0]
        bpp = struct.unpack('<H', bmp_data[28:30])[0]
        
        print(f"File size: {file_size}")
        print(f"Pixel data offset: {offset_bits}")
        print(f"DIB header size: {dib_size}")
        print(f"Width: {width}")
        print(f"Height: {height}")
        print(f"Planes: {planes}")
        print(f"Bits per pixel: {bpp}")

if __name__ == '__main__':
    find_and_extract_bmp(r'D:\mission-git-hackss\flight_record.dat')
