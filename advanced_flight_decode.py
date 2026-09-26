#!/usr/bin/env python3
"""
Advanced decoding - look at LSBs, coordinate precision, etc.
"""

import struct
import binascii

def advanced_analysis(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Extract all coordinate bytes
    print("=== Extracting coordinate byte patterns ===")
    offset = 256
    coord_bytes = []
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            # Get the 24 bytes of coordinate data (3 doubles)
            coord_data = data[offset+12:offset+36]
            coord_bytes.append(coord_data)
            offset += 40
        else:
            offset += 1
    
    print(f"Extracted {len(coord_bytes)} coordinate blocks")
    
    # Method 1: Look at LSBs of each double
    print("\n=== Method 1: LSBs of coordinate doubles ===")
    lsb_bits = []
    for coords in coord_bytes[:100]:
        for i in range(0, 24, 8):
            double_bytes = coords[i:i+8]
            # Get LSB of the last byte
            lsb = double_bytes[-1] & 1
            lsb_bits.append(lsb)
    
    # Convert bits to bytes
    lsb_bytes = []
    for i in range(0, len(lsb_bits), 8):
        if i + 8 <= len(lsb_bits):
            byte_val = 0
            for j in range(8):
                byte_val |= (lsb_bits[i+j] << j)
            lsb_bytes.append(byte_val)
    
    print(f"LSB bytes (first 50): {bytes(lsb_bytes[:50])}")
    print(f"LSB as ASCII: {''.join(chr(b) if 32 <= b < 127 else '.' for b in lsb_bytes[:100])}")
    
    # Method 2: XOR consecutive coordinates
    print("\n=== Method 2: XOR consecutive coordinate blocks ===")
    xor_results = []
    for i in range(len(coord_bytes) - 1):
        xor_block = bytes([a ^ b for a, b in zip(coord_bytes[i], coord_bytes[i+1])])
        xor_results.append(xor_block)
    
    # Look for patterns
    for i, xor_block in enumerate(xor_results[:10]):
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in xor_block)
        print(f"XOR {i}: {xor_block.hex()} -> {ascii_str}")
    
    # Method 3: Look at the fractional parts
    print("\n=== Method 3: Fractional parts of coordinates ===")
    offset = 256
    fractions = []
    
    for _ in range(min(20, len(coord_bytes))):
        if offset < len(data) - 40:
            if data[offset] == 0x01 and data[offset+1] == 0x55:
                val1 = struct.unpack('<d', data[offset+12:offset+20])[0]
                val2 = struct.unpack('<d', data[offset+20:offset+28])[0]
                val3 = struct.unpack('<d', data[offset+28:offset+36])[0]
                
                # Get fractional parts
                frac1 = val1 - int(val1)
                frac2 = val2 - int(val2)
                frac3 = val3 - int(val3)
                
                fractions.append((frac1, frac2, frac3))
                offset += 40
    
    for i, (f1, f2, f3) in enumerate(fractions):
        print(f"Record {i+1}: {f1:.10f}, {f2:.10f}, {f3:.10f}")
    
    # Method 4: Check if there's data after the records
    print("\n=== Method 4: Data after records ===")
    # Find where records end
    last_record_offset = 256
    while last_record_offset < len(data) - 40:
        if data[last_record_offset] == 0x01 and data[last_record_offset+1] == 0x55:
            last_record_offset += 40
        else:
            break
    
    # Actually, let's find the LAST occurrence of the record marker
    last_marker = data.rfind(b'\x01\x55\x24\x00')
    if last_marker != -1:
        print(f"Last record marker at: {last_marker}")
        print(f"Data after last record: {len(data) - (last_marker + 40)} bytes")
        
        if last_marker + 40 < len(data):
            trailing_data = data[last_marker + 40:]
            print(f"Trailing data (hex): {trailing_data[:200].hex()}")
            print(f"Trailing data (ASCII): {''.join(chr(b) if 32 <= b < 127 else '.' for b in trailing_data[:200])}")
            
            # Check if it contains flag
            if b'Kaal{' in trailing_data:
                idx = trailing_data.index(b'Kaal{')
                print(f"\n!!! FLAG FOUND at offset {last_marker + 40 + idx} !!!")
                print(trailing_data[idx:idx+100])
    
    # Method 5: Try to decode the entire file as different formats
    print("\n=== Method 5: Check for embedded archive ===")
    # Look for common archive signatures
    if b'PK\x03\x04' in data:
        print("ZIP signature found!")
        idx = data.index(b'PK\x03\x04')
        print(f"At offset: {idx}")
    
    # Method 6: Entropy analysis - look for compressed/encrypted sections
    print("\n=== Method 6: Looking for high-entropy sections ===")
    chunk_size = 1000
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        # Simple entropy: count unique bytes
        unique = len(set(chunk))
        if unique > 200:  # High entropy
            print(f"High entropy at offset {i}: {unique} unique bytes")
            # Check if it contains readable text
            ascii_count = sum(1 for b in chunk if 32 <= b < 127)
            if ascii_count > chunk_size * 0.5:
                print(f"  Contains {ascii_count} ASCII chars")
                print(f"  Sample: {''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk[:100])}")

if __name__ == '__main__':
    advanced_analysis(r'D:\mission-git-hackss\flight_record.dat')
