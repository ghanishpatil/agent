#!/usr/bin/env python3
"""
Analyze flight_record.dat - reverse engineering challenge
The file appears to be a binary flight data recorder
"""

import struct
import sys

def analyze_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    print(f"Magic bytes: {data[:4].hex()}")
    
    # Look for patterns
    print("\n=== Looking for ASCII strings ===")
    ascii_strings = []
    current = []
    for i, byte in enumerate(data):
        if 32 <= byte <= 126:  # Printable ASCII
            current.append(chr(byte))
        else:
            if len(current) >= 4:
                ascii_strings.append(''.join(current))
            current = []
    
    if current and len(current) >= 4:
        ascii_strings.append(''.join(current))
    
    for s in ascii_strings[:50]:
        print(f"  {s}")
    
    # Look for flag pattern
    print("\n=== Searching for flag pattern ===")
    flag_patterns = [b'Kaal{', b'kaal{', b'KAAL{', b'flag{', b'FLAG{']
    for pattern in flag_patterns:
        if pattern in data:
            idx = data.index(pattern)
            print(f"Found {pattern} at offset {idx}")
            print(f"Context: {data[idx:idx+100]}")
    
    # Analyze structure - looks like records
    print("\n=== Analyzing binary structure ===")
    offset = 4  # Skip magic bytes
    
    # Skip zeros
    while offset < len(data) and data[offset] == 0:
        offset += 1
    
    print(f"Data starts at offset: {offset}")
    
    # Try to parse records
    record_count = 0
    while offset < len(data) - 50:
        try:
            # Check for record marker
            if data[offset] == 0x01 and data[offset+1] == 0x55:
                record_count += 1
                if record_count <= 10:
                    print(f"\nRecord {record_count} at offset {offset}:")
                    record_data = data[offset:offset+40]
                    print(f"  Hex: {record_data.hex()}")
                    
                    # Try to parse as structured data
                    # Looks like: marker(2) + type(2) + timestamp(4) + padding(4) + doubles(3*8)
                    marker = struct.unpack('<H', data[offset:offset+2])[0]
                    rec_type = struct.unpack('<H', data[offset+2:offset+4])[0]
                    timestamp = struct.unpack('<I', data[offset+4:offset+8])[0]
                    
                    print(f"  Marker: 0x{marker:04x}, Type: 0x{rec_type:04x}, Timestamp: {timestamp}")
                    
                    # Try to parse as doubles (coordinates?)
                    if offset + 32 <= len(data):
                        val1 = struct.unpack('<d', data[offset+12:offset+20])[0]
                        val2 = struct.unpack('<d', data[offset+20:offset+28])[0]
                        val3 = struct.unpack('<d', data[offset+28:offset+36])[0]
                        print(f"  Values: {val1:.6f}, {val2:.6f}, {val3:.6f}")
                
                offset += 40  # Move to next record
            else:
                offset += 1
        except:
            offset += 1
    
    print(f"\nTotal records found: {record_count}")
    
    # Check end of file
    print("\n=== End of file ===")
    print(f"Last 200 bytes:\n{data[-200:].hex()}")
    print(f"Last 200 bytes (ASCII attempt):")
    for byte in data[-200:]:
        if 32 <= byte <= 126:
            print(chr(byte), end='')
        else:
            print('.', end='')
    print()

if __name__ == '__main__':
    analyze_file(r'D:\mission-git-hackss\flight_record.dat')
