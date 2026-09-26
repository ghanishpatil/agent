#!/usr/bin/env python3
"""
Deep analysis of flight_record.dat
Try different interpretations of the binary data
"""

import struct
import binascii

def hex_dump(data, offset=0, length=None):
    if length:
        data = data[offset:offset+length]
    else:
        data = data[offset:]
    
    for i in range(0, len(data), 16):
        hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f'{offset+i:08x}  {hex_str:<48}  {ascii_str}')

def analyze_deep(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print("=== File Header ===")
    hex_dump(data, 0, 256)
    
    print("\n=== First few records ===")
    hex_dump(data, 256, 400)
    
    # Check if there's hidden data in the "zeros" section
    print("\n=== Checking header zeros for hidden data ===")
    header_section = data[4:256]
    non_zero = [i for i, b in enumerate(header_section) if b != 0]
    if non_zero:
        print(f"Non-zero bytes found at positions: {non_zero}")
        for pos in non_zero:
            print(f"  Position {pos+4}: 0x{header_section[pos]:02x}")
    else:
        print("All zeros in header section")
    
    # Try XOR decoding
    print("\n=== Trying XOR with common keys ===")
    for key in [0x55, 0xAA, 0xFF, 0x42]:
        xored = bytes([b ^ key for b in data[:100]])
        if b'Kaal{' in xored or b'flag' in xored:
            print(f"XOR key 0x{key:02x} found something!")
            print(xored)
    
    # Check for embedded files
    print("\n=== Checking for embedded files ===")
    signatures = {
        b'PK\x03\x04': 'ZIP',
        b'\x1f\x8b': 'GZIP',
        b'%PDF': 'PDF',
        b'\x89PNG': 'PNG',
        b'GIF8': 'GIF',
        b'\xff\xd8\xff': 'JPEG',
        b'BM': 'BMP',
        b'Rar!': 'RAR',
        b'7z\xbc\xaf': '7Z',
        b'\x50\x4b\x03\x04': 'ZIP',
    }
    
    for sig, ftype in signatures.items():
        if sig in data:
            idx = data.index(sig)
            print(f"Found {ftype} signature at offset {idx}")
            hex_dump(data, idx, 64)
    
    # Look for strings in the entire file
    print("\n=== All strings (length >= 6) ===")
    strings = []
    current = []
    for byte in data:
        if 32 <= byte <= 126:
            current.append(chr(byte))
        else:
            if len(current) >= 6:
                strings.append(''.join(current))
            current = []
    if current and len(current) >= 6:
        strings.append(''.join(current))
    
    for s in strings:
        print(f"  {s}")
    
    # Check record structure more carefully
    print("\n=== Detailed record analysis ===")
    offset = 256
    for rec_num in range(5):
        if offset + 40 > len(data):
            break
        
        print(f"\nRecord {rec_num + 1}:")
        rec_data = data[offset:offset+40]
        hex_dump(rec_data, 0, 40)
        
        # Try different interpretations
        print("  Interpretations:")
        print(f"    Bytes 0-1: {struct.unpack('<H', rec_data[0:2])[0]} (0x{rec_data[0]:02x}{rec_data[1]:02x})")
        print(f"    Bytes 2-3: {struct.unpack('<H', rec_data[2:4])[0]} (0x{rec_data[2]:02x}{rec_data[3]:02x})")
        print(f"    Bytes 4-7: {struct.unpack('<I', rec_data[4:8])[0]}")
        print(f"    Bytes 8-11: {struct.unpack('<I', rec_data[8:12])[0]}")
        
        # Check if bytes 36-39 are interesting
        if offset + 40 <= len(data):
            next_marker = data[offset+36:offset+40]
            print(f"    Bytes 36-39: {next_marker.hex()} = {struct.unpack('<I', next_marker)[0]}")
        
        offset += 40
    
    # Check the very end of file
    print("\n=== Last 500 bytes ===")
    hex_dump(data, len(data)-500, 500)

if __name__ == '__main__':
    analyze_deep(r'D:\mission-git-hackss\flight_record.dat')
