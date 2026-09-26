#!/usr/bin/env python3
"""
Final comprehensive analysis - check EVERYTHING
"""

import struct

def final_analysis(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print("=== Comprehensive File Analysis ===\n")
    
    # 1. Check every possible offset for the flag
    print("1. Brute force search for 'Kaal{' at every offset...")
    for i in range(len(data) - 5):
        if data[i:i+5] == b'Kaal{':
            print(f"   FOUND at offset {i}!")
            end = data.find(b'}', i)
            if end != -1:
                print(f"   FLAG: {data[i:end+1]}")
                return
    print("   Not found\n")
    
    # 2. Check with different case
    print("2. Checking case variations...")
    for pattern in [b'kaal{', b'KAAL{', b'Kaal(', b'kaal(']:
        if pattern in data:
            idx = data.index(pattern)
            print(f"   Found {pattern} at {idx}: {data[idx:idx+50]}")
    print("   None found\n")
    
    # 3. Extract and concatenate specific fields from records
    print("3. Extracting all record fields...")
    offset = 256
    
    # Try extracting different field combinations
    for field_name, field_offset, field_size in [
        ("Marker", 0, 2),
        ("Type", 2, 2),
        ("Timestamp", 4, 4),
        ("Field1", 8, 4),
        ("Lat", 12, 8),
        ("Lon", 20, 8),
        ("Alt", 28, 8),
        ("Last", 36, 4),
    ]:
        extracted = []
        temp_offset = 256
        count = 0
        
        while temp_offset < len(data) - 40 and count < 1501:
            if data[temp_offset] == 0x01 and data[temp_offset+1] == 0x55:
                field_data = data[temp_offset + field_offset:temp_offset + field_offset + field_size]
                extracted.extend(field_data)
                temp_offset += 40
                count += 1
            else:
                temp_offset += 1
        
        extracted_bytes = bytes(extracted)
        if b'Kaal{' in extracted_bytes:
            idx = extracted_bytes.index(b'Kaal{')
            end = extracted_bytes.find(b'}', idx)
            if end != -1:
                print(f"   FLAG FOUND in {field_name} field!")
                print(f"   FLAG: {extracted_bytes[idx:end+1].decode('ascii', errors='ignore')}")
                return
    
    print("   No flag in any field\n")
    
    # 4. Try XOR with different keys
    print("4. Trying XOR with various keys...")
    test_data = data[:50000]  # Test first 50KB
    
    for key in [0x55, 0xAA, 0xFF, 0x42, 0x13, 0x37]:
        xored = bytes([b ^ key for b in test_data])
        if b'Kaal{' in xored:
            idx = xored.index(b'Kaal{')
            end = xored.find(b'}', idx)
            if end != -1:
                print(f"   FLAG FOUND with XOR key 0x{key:02x}!")
                print(f"   FLAG: {xored[idx:end+1].decode('ascii', errors='ignore')}")
                return
    
    print("   No flag with XOR\n")
    
    # 5. Check if it's base64 encoded
    print("5. Checking for base64 encoding...")
    import base64
    import string
    
    # Extract base64-like characters
    b64_chars = ''.join(chr(b) for b in data if chr(b) in string.ascii_letters + string.digits + '+/=')
    
    if len(b64_chars) > 100:
        # Try to decode chunks
        for start in range(0, min(len(b64_chars), 10000), 100):
            chunk = b64_chars[start:start+1000]
            # Pad if necessary
            padding = (4 - len(chunk) % 4) % 4
            chunk += '=' * padding
            
            try:
                decoded = base64.b64decode(chunk)
                if b'Kaal{' in decoded:
                    idx = decoded.index(b'Kaal{')
                    end = decoded.find(b'}', idx)
                    if end != -1:
                        print(f"   FLAG FOUND in base64!")
                        print(f"   FLAG: {decoded[idx:end+1].decode('ascii', errors='ignore')}")
                        return
            except:
                pass
    
    print("   No flag in base64\n")
    
    # 6. Check the header section more carefully
    print("6. Analyzing header (bytes 0-255)...")
    header = data[:256]
    
    # Check for hidden data in "zero" section
    for i in range(4, 256):
        if header[i] != 0:
            print(f"   Non-zero byte at offset {i}: 0x{header[i]:02x}")
    
    # Try to decode header as different structures
    if all(b == 0 for b in header[4:256]):
        print("   Header is all zeros after magic\n")
    
    # 7. Look at the end of file
    print("7. Checking end of file...")
    tail = data[-1000:]
    if b'Kaal{' in tail:
        idx = tail.index(b'Kaal{')
        end = tail.find(b'}', idx)
        if end != -1:
            print(f"   FLAG FOUND at end of file!")
            print(f"   FLAG: {tail[idx:end+1].decode('ascii', errors='ignore')}")
            return
    
    print("   No flag at end\n")
    
    # 8. Try interpreting the entire file as a different format
    print("8. Trying alternative file formats...")
    
    # Check if it's a ZIP (even if corrupted)
    if b'PK' in data:
        print("   ZIP signature found")
    
    # Check for ELF
    if b'\x7fELF' in data:
        print("   ELF signature found")
    
    # Check for PE
    if b'MZ' in data and b'PE\x00\x00' in data:
        print("   PE executable found")
    
    print("\n=== ANALYSIS COMPLETE - NO FLAG FOUND ===")
    print("The flag might be:")
    print("  - Encoded in the GPS path itself (visual)")
    print("  - Requires special tools or knowledge")
    print("  - Hidden in metadata or file system structures")
    print("  - Encrypted with a key we don't have")

if __name__ == '__main__':
    final_analysis(r'D:\mission-git-hackss\flight_record.dat')
