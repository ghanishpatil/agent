#!/usr/bin/env python3
"""
Ultimate decoding attempt - try EVERYTHING
"""

import struct
import zlib
import base64

def ultimate_decode(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes\n")
    
    # 1. Direct string search with variations
    print("=== Direct string search ===")
    patterns = [b'Kaal{', b'kaal{', b'KAAL{', b'flag{', b'FLAG{', b'CTF{']
    for pattern in patterns:
        if pattern in data:
            idx = data.index(pattern)
            print(f"Found {pattern} at {idx}: {data[idx:idx+100]}")
            return
    print("No direct flag found\n")
    
    # 2. Try decompression
    print("=== Trying decompression ===")
    for start_offset in [0, 4, 256]:
        try:
            decompressed = zlib.decompress(data[start_offset:])
            print(f"Decompressed from offset {start_offset}!")
            if b'Kaal{' in decompressed:
                idx = decompressed.index(b'Kaal{')
                print(f"FLAG: {decompressed[idx:idx+100]}")
                return
        except:
            pass
    print("No decompression worked\n")
    
    # 3. Extract bytes from specific record positions
    print("=== Extracting from record byte positions ===")
    offset = 256
    
    for byte_offset in range(40):
        extracted = []
        temp_offset = 256
        count = 0
        
        while temp_offset < len(data) - 40 and count < 500:
            if data[temp_offset] == 0x01 and data[temp_offset+1] == 0x55:
                if temp_offset + byte_offset < len(data):
                    extracted.append(data[temp_offset + byte_offset])
                temp_offset += 40
                count += 1
            else:
                temp_offset += 1
        
        # Check if this forms a flag
        extracted_bytes = bytes(extracted)
        if b'Kaal{' in extracted_bytes:
            idx = extracted_bytes.index(b'Kaal{')
            print(f"FLAG found at byte offset {byte_offset}!")
            print(f"FLAG: {extracted_bytes[idx:idx+100]}")
            return
    
    print("No flag in individual byte positions\n")
    
    # 4. Try every possible byte extraction pattern
    print("=== Trying multi-byte patterns ===")
    # Extract bytes 2-3 from each record (the type field)
    offset = 256
    type_bytes = []
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            type_bytes.append(data[offset+2])
            type_bytes.append(data[offset+3])
            offset += 40
        else:
            offset += 1
    
    type_data = bytes(type_bytes)
    if b'Kaal{' in type_data:
        idx = type_data.index(b'Kaal{')
        print(f"FLAG in type bytes: {type_data[idx:idx+100]}")
        return
    
    # 5. Try interpreting the doubles as packed data
    print("=== Extracting from double precision fields ===")
    offset = 256
    double_bytes = []
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            # Get all three doubles
            double_bytes.extend(data[offset+12:offset+36])
            offset += 40
        else:
            offset += 1
    
    double_data = bytes(double_bytes)
    if b'Kaal{' in double_data:
        idx = double_data.index(b'Kaal{')
        print(f"FLAG in double data: {double_data[idx:idx+100]}")
        return
    
    # 6. Check if the timestamp sequence encodes something
    print("=== Analyzing timestamp sequence ===")
    offset = 256
    timestamps = []
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            ts = struct.unpack('<I', data[offset+4:offset+8])[0]
            timestamps.append(ts)
            offset += 40
        else:
            offset += 1
    
    print(f"First 20 timestamps: {timestamps[:20]}")
    print(f"Timestamp differences: {[timestamps[i+1]-timestamps[i] for i in range(min(10, len(timestamps)-1))]}")
    
    # Check if timestamps encode ASCII
    ts_chars = []
    for ts in timestamps:
        # Try each byte of the timestamp
        for i in range(4):
            byte = (ts >> (i*8)) & 0xFF
            if byte != 0:
                ts_chars.append(byte)
    
    ts_data = bytes(ts_chars)
    if b'Kaal{' in ts_data:
        idx = ts_data.index(b'Kaal{')
        print(f"FLAG in timestamps: {ts_data[idx:idx+100]}")
        return
    
    # 7. Try reading the file as different formats
    print("\n=== Trying alternative interpretations ===")
    
    # Maybe it's a SQLite database?
    if b'SQLite' in data:
        print("SQLite database detected!")
    
    # Maybe it's a custom format with a different structure?
    # Try reading past the records
    last_record = data.rfind(b'\x01\x55\x24\x00')
    if last_record != -1:
        print(f"Last record at: {last_record}")
        remaining = data[last_record+40:]
        print(f"Bytes after last record: {len(remaining)}")
        if len(remaining) > 0:
            print(f"Remaining data: {remaining[:200]}")
            if b'Kaal{' in remaining:
                idx = remaining.index(b'Kaal{')
                print(f"FLAG: {remaining[idx:idx+100]}")
                return
    
    # 8. Check the magic number more carefully
    print("\n=== Magic number analysis ===")
    magic = data[:4]
    print(f"Magic: {magic.hex()} = {magic}")
    
    # 0x55AA is a boot sector signature
    # Maybe this is a disk image?
    if magic[:2] == b'\x55\xaa':
        print("This looks like a boot sector!")
        # Try to parse as FAT/MBR
        
    # 9. Try every XOR key
    print("\n=== Trying XOR decryption ===")
    for key in range(256):
        xored = bytes([b ^ key for b in data[:10000]])
        if b'Kaal{' in xored:
            idx = xored.index(b'Kaal{')
            print(f"FLAG found with XOR key 0x{key:02x}!")
            print(f"FLAG: {xored[idx:idx+100]}")
            return
    
    print("\n=== No flag found with any method ===")

if __name__ == '__main__':
    ultimate_decode(r'D:\mission-git-hackss\flight_record.dat')
