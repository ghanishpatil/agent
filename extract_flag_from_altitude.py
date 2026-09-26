#!/usr/bin/env python3
"""
Extract the flag from altitude integer parts
"""

import struct

def extract_flag(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Extract all altitude values
    offset = 256
    alt_values = []
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            alt = struct.unpack('<d', data[offset+28:offset+36])[0]
            alt_values.append(alt)
            offset += 40
        else:
            offset += 1
    
    print(f"Extracted {len(alt_values)} altitude values\n")
    
    # Method 1: Extract ASCII from integer parts
    print("=== Method 1: Integer parts as ASCII ===")
    message1 = []
    for alt in alt_values:
        int_part = int(alt)
        # Extract bytes in little-endian order
        chars = []
        temp = int_part
        while temp > 0:
            byte = temp & 0xFF
            if byte != 0:  # Skip null bytes
                chars.insert(0, chr(byte) if 32 <= byte < 127 else '.')
            temp >>= 8
        message1.extend(chars)
    
    msg1_str = ''.join(message1)
    print(f"Message (first 500 chars): {msg1_str[:500]}")
    
    if 'Kaal{' in msg1_str:
        idx = msg1_str.index('Kaal{')
        end_idx = msg1_str.find('}', idx)
        if end_idx != -1:
            print(f"\n!!! FLAG FOUND !!!")
            print(f"FLAG: {msg1_str[idx:end_idx+1]}")
            return
    
    # Method 2: Extract only the last byte of each integer
    print("\n=== Method 2: Last byte of each integer ===")
    message2 = []
    for alt in alt_values:
        int_part = int(alt)
        last_byte = int_part & 0xFF
        if 32 <= last_byte < 127:
            message2.append(chr(last_byte))
    
    msg2_str = ''.join(message2)
    print(f"Message: {msg2_str[:500]}")
    
    if 'Kaal{' in msg2_str:
        idx = msg2_str.index('Kaal{')
        end_idx = msg2_str.find('}', idx)
        if end_idx != -1:
            print(f"\n!!! FLAG FOUND !!!")
            print(f"FLAG: {msg2_str[idx:end_idx+1]}")
            return
    
    # Method 3: Extract from fractional parts
    print("\n=== Method 3: Fractional parts ===")
    message3 = []
    for alt in alt_values:
        frac_part = alt - int(alt)
        # Multiply by large number to get integer
        frac_int = int(frac_part * 1000000000)
        
        # Extract bytes
        chars = []
        temp = frac_int
        for _ in range(4):
            byte = temp & 0xFF
            if 32 <= byte < 127:
                chars.append(chr(byte))
            temp >>= 8
        message3.extend(chars)
    
    msg3_str = ''.join(message3)
    print(f"Message (first 500 chars): {msg3_str[:500]}")
    
    if 'Kaal{' in msg3_str:
        idx = msg3_str.index('Kaal{')
        end_idx = msg3_str.find('}', idx)
        if end_idx != -1:
            print(f"\n!!! FLAG FOUND !!!")
            print(f"FLAG: {msg3_str[idx:end_idx+1]}")
            return
    
    # Method 4: Look at the raw bytes of the altitude field
    print("\n=== Method 4: Raw altitude bytes ===")
    offset = 256
    raw_bytes = []
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            # Get the 8 bytes of the altitude double
            raw_bytes.extend(data[offset+28:offset+36])
            offset += 40
        else:
            offset += 1
    
    raw_data = bytes(raw_bytes)
    
    # Search for flag in raw bytes
    if b'Kaal{' in raw_data:
        idx = raw_data.index(b'Kaal{')
        end_idx = raw_data.find(b'}', idx)
        if end_idx != -1:
            print(f"\n!!! FLAG FOUND in raw bytes !!!")
            print(f"FLAG: {raw_data[idx:end_idx+1].decode('ascii', errors='ignore')}")
            return
        else:
            print(f"\n!!! FLAG FOUND in raw bytes (no end) !!!")
            print(f"FLAG: {raw_data[idx:idx+100]}")
            return
    
    # Print raw bytes as ASCII
    raw_ascii = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw_bytes[:500])
    print(f"Raw bytes as ASCII (first 500): {raw_ascii}")
    
    print("\n=== No flag found ===")

if __name__ == '__main__':
    extract_flag(r'D:\mission-git-hackss\flight_record.dat')
