#!/usr/bin/env python3
"""
Final attempt - try everything systematically
"""

import struct
import string

def comprehensive_decode(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    print(f"Magic: {data[:4].hex()}")
    
    # 1. Check every byte for ASCII patterns
    print("\n=== Searching for 'Kaal{' pattern ===")
    for i in range(len(data) - 5):
        if data[i:i+5] == b'Kaal{':
            print(f"Found at offset {i}!")
            print(f"Context: {data[i:i+100]}")
            return
    
    # 2. Try ROT13, Caesar cipher on any text
    print("\n=== Trying simple ciphers on extracted text ===")
    text_bytes = [b for b in data if 32 <= b < 127]
    text = ''.join(chr(b) for b in text_bytes[:500])
    print(f"Extracted text (first 500 chars): {text}")
    
    # Try Caesar shifts
    for shift in range(1, 26):
        shifted = ''
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted += chr((ord(char) - base + shift) % 26 + base)
            else:
                shifted += char
        
        if 'Kaal{' in shifted or 'kaal{' in shifted:
            print(f"\nCaesar shift {shift} found flag!")
            print(shifted[:200])
            return
    
    # 3. Extract data from specific record fields
    print("\n=== Extracting all record field bytes ===")
    offset = 256
    all_bytes = []
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            # Try different byte positions
            # Bytes 4-7 (timestamp)
            timestamp = struct.unpack('<I', data[offset+4:offset+8])[0]
            
            # Convert timestamp to bytes and check
            ts_bytes = struct.pack('<I', timestamp)
            all_bytes.extend(ts_bytes)
            
            offset += 40
        else:
            offset += 1
    
    # Check if these bytes contain the flag
    all_bytes_data = bytes(all_bytes)
    if b'Kaal{' in all_bytes_data:
        idx = all_bytes_data.index(b'Kaal{')
        print(f"Flag found in timestamp bytes at position {idx}!")
        print(all_bytes_data[idx:idx+100])
        return
    
    # 4. Try interpreting coordinates as encoded data
    print("\n=== Coordinate encoding analysis ===")
    offset = 256
    coord_ints = []
    
    for _ in range(100):
        if offset < len(data) - 40:
            if data[offset] == 0x01 and data[offset+1] == 0x55:
                # Get coordinates as raw bytes
                lat_bytes = data[offset+12:offset+20]
                lon_bytes = data[offset+20:offset+28]
                alt_bytes = data[offset+28:offset+36]
                
                # Try to extract meaningful data
                # Maybe the mantissa contains ASCII?
                lat_val = struct.unpack('<d', lat_bytes)[0]
                lon_val = struct.unpack('<d', lon_bytes)[0]
                alt_val = struct.unpack('<d', alt_bytes)[0]
                
                # Get the bytes after decimal point
                lat_frac = lat_val - int(lat_val)
                lon_frac = lon_val - int(lon_val)
                alt_frac = alt_val - int(alt_val)
                
                # Multiply by large number to get integer representation
                lat_int = int(lat_frac * 1000000000)
                lon_int = int(lon_frac * 1000000000)
                alt_int = int(alt_frac * 1000000000)
                
                coord_ints.append((lat_int, lon_int, alt_int))
                
                offset += 40
    
    # Try to extract ASCII from these integers
    for method in ['lat', 'lon', 'alt']:
        print(f"\n  Trying {method} fractional parts:")
        chars = []
        for lat_int, lon_int, alt_int in coord_ints:
            if method == 'lat':
                val = lat_int
            elif method == 'lon':
                val = lon_int
            else:
                val = alt_int
            
            # Try different byte extractions
            for i in range(4):
                byte = (val >> (i * 8)) & 0xFF
                if 32 <= byte < 127:
                    chars.append(chr(byte))
        
        result = ''.join(chars[:200])
        if 'Kaal' in result or 'flag' in result:
            print(f"    FOUND: {result}")
            return
        print(f"    Sample: {result[:100]}")
    
    # 5. Check the header more carefully
    print("\n=== Detailed header analysis ===")
    print(f"Bytes 0-3: {data[0:4].hex()}")
    print(f"Bytes 4-255: All zeros? {all(b == 0 for b in data[4:256])}")
    
    # 6. Try binwalk-style signature scanning
    print("\n=== Signature scanning ===")
    signatures = [
        (b'Kaal{', 'Flag'),
        (b'flag{', 'Flag'),
        (b'CTF{', 'Flag'),
        (b'PK\x03\x04', 'ZIP'),
        (b'\x1f\x8b\x08', 'GZIP'),
        (b'%PDF', 'PDF'),
        (b'\x89PNG', 'PNG'),
        (b'\xff\xd8\xff', 'JPEG'),
        (b'GIF8', 'GIF'),
        (b'BM', 'BMP'),
        (b'MZ', 'EXE'),
        (b'\x7fELF', 'ELF'),
    ]
    
    for sig, name in signatures:
        idx = data.find(sig)
        if idx != -1:
            print(f"  {name} signature at offset {idx}")
            print(f"    Context: {data[idx:idx+50].hex()}")
    
    # 7. Try to decode as base64
    print("\n=== Base64 decode attempt ===")
    import base64
    # Extract only base64-valid characters
    b64_chars = ''.join(chr(b) for b in data if chr(b) in string.ascii_letters + string.digits + '+/=')
    if len(b64_chars) > 100:
        try:
            decoded = base64.b64decode(b64_chars[:1000])
            if b'Kaal{' in decoded:
                print("Flag found in base64 decoded data!")
                print(decoded)
                return
        except:
            pass
    
    # 8. Check if the file itself is encoded
    print("\n=== Checking for file-level encoding ===")
    # Try XOR with the magic bytes
    xor_key = data[0]
    xored = bytes([b ^ xor_key for b in data[:1000]])
    if b'Kaal{' in xored:
        print(f"Flag found with XOR key 0x{xor_key:02x}!")
        idx = xored.index(b'Kaal{')
        print(xored[idx:idx+100])
        return

if __name__ == '__main__':
    comprehensive_decode(r'D:\mission-git-hackss\flight_record.dat')
