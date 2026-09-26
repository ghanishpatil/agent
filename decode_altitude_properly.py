#!/usr/bin/env python3
"""
Properly decode the altitude field - it contains the flag!
"""

import struct

def decode_altitude(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Extract altitude bytes directly
    offset = 256
    altitude_bytes = []
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            # Altitude is at offset+28 to offset+36 (8 bytes, double)
            alt_data = data[offset+28:offset+36]
            altitude_bytes.extend(alt_data)
            offset += 40
        else:
            offset += 1
    
    print(f"Extracted {len(altitude_bytes)} bytes from altitude fields")
    
    # Convert to string
    altitude_data = bytes(altitude_bytes)
    
    # Try as ASCII
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in altitude_data)
    print(f"\nAltitude data as ASCII (first 500 chars):")
    print(ascii_str[:500])
    
    # Search for flag
    if b'Kaal{' in altitude_data:
        idx = altitude_data.index(b'Kaal{')
        print(f"\n!!! FLAG FOUND at byte {idx} !!!")
        
        # Extract the flag
        flag_end = altitude_data.find(b'}', idx)
        if flag_end != -1:
            flag = altitude_data[idx:flag_end+1]
            print(f"\nFLAG: {flag.decode('ascii', errors='ignore')}")
        else:
            print(f"\nFLAG (first 100 bytes): {altitude_data[idx:idx+100]}")
    else:
        print("\nNo flag found in altitude data")
    
    # Also try the raw bytes
    print("\n=== Raw altitude bytes (first 200) ===")
    print(altitude_data[:200].hex())
    
    # Try different interpretations
    print("\n=== Trying different byte orders ===")
    
    # Maybe we need to read the doubles differently?
    offset = 256
    alt_values = []
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            # Read as double
            alt = struct.unpack('<d', data[offset+28:offset+36])[0]
            alt_values.append(alt)
            offset += 40
        else:
            offset += 1
    
    print(f"\nFirst 20 altitude values:")
    for i, alt in enumerate(alt_values[:20]):
        print(f"  {i+1}. {alt:.10f}")
    
    # Try to extract the integer part and fractional part separately
    print("\n=== Analyzing altitude structure ===")
    for i, alt in enumerate(alt_values[:10]):
        int_part = int(alt)
        frac_part = alt - int_part
        
        print(f"\nAltitude {i+1}: {alt}")
        print(f"  Integer: {int_part}")
        print(f"  Fraction: {frac_part:.10f}")
        
        # Try to decode integer part as ASCII
        chars = []
        temp = int_part
        while temp > 0:
            byte = temp & 0xFF
            if 32 <= byte < 127:
                chars.insert(0, chr(byte))
            temp >>= 8
        
        if chars:
            print(f"  Integer as ASCII: {''.join(chars)}")

if __name__ == '__main__':
    decode_altitude(r'D:\mission-git-hackss\flight_record.dat')
