#!/usr/bin/env python3
"""
Nuclear option - try EVERY possible decoding method
"""

import struct

def nuclear_decode(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print("=== NUCLEAR DECODING ATTEMPT ===\n")
    
    # Extract all records
    records = []
    offset = 256
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            rec = {
                'raw': data[offset:offset+40],
                'marker': struct.unpack('<H', data[offset:offset+2])[0],
                'type': struct.unpack('<H', data[offset+2:offset+4])[0],
                'timestamp': struct.unpack('<I', data[offset+4:offset+8])[0],
                'field1': struct.unpack('<I', data[offset+8:offset+12])[0],
                'lat': struct.unpack('<d', data[offset+12:offset+20])[0],
                'lon': struct.unpack('<d', data[offset+20:offset+28])[0],
                'alt': struct.unpack('<d', data[offset+28:offset+36])[0],
                'last': struct.unpack('<I', data[offset+36:offset+40])[0],
            }
            records.append(rec)
            offset += 40
        else:
            offset += 1
    
    print(f"Extracted {len(records)} records\n")
    
    # Try extracting flag from every possible combination
    methods = []
    
    # Method: Concatenate specific bytes from each record
    for byte_pos in range(40):
        extracted = bytes([r['raw'][byte_pos] for r in records])
        if b'Kaal{' in extracted:
            idx = extracted.index(b'Kaal{')
            end = extracted.find(b'}', idx)
            if end != -1:
                flag = extracted[idx:end+1].decode('ascii', errors='ignore')
                print(f"!!! FLAG FOUND at byte position {byte_pos} !!!")
                print(f"FLAG: {flag}")
                return flag
    
    # Method: Extract from timestamp differences
    ts_diffs = [records[i+1]['timestamp'] - records[i]['timestamp'] for i in range(len(records)-1)]
    ts_diff_bytes = b''.join(struct.pack('<i', d) for d in ts_diffs if -2147483648 <= d <= 2147483647)
    if b'Kaal{' in ts_diff_bytes:
        idx = ts_diff_bytes.index(b'Kaal{')
        end = ts_diff_bytes.find(b'}', idx)
        if end != -1:
            flag = ts_diff_bytes[idx:end+1].decode('ascii', errors='ignore')
            print(f"!!! FLAG FOUND in timestamp differences !!!")
            print(f"FLAG: {flag}")
            return flag
    
    # Method: XOR consecutive records
    for i in range(len(records) - 1):
        xored = bytes([a ^ b for a, b in zip(records[i]['raw'], records[i+1]['raw'])])
        if b'Kaal{' in xored:
            idx = xored.index(b'Kaal{')
            end = xored.find(b'}', idx)
            if end != -1:
                flag = xored[idx:end+1].decode('ascii', errors='ignore')
                print(f"!!! FLAG FOUND in XOR of records {i} and {i+1} !!!")
                print(f"FLAG: {flag}")
                return flag
    
    # Method: Interpret coordinates as character codes
    for field in ['lat', 'lon', 'alt']:
        chars = []
        for r in records:
            val = int(r[field])
            # Try modulo operations
            for mod in [256, 128, 95]:
                char_code = val % mod
                if 32 <= char_code < 127:
                    chars.append(chr(char_code))
                    break
        
        result = ''.join(chars)
        if 'Kaal{' in result:
            idx = result.index('Kaal{')
            end = result.find('}', idx)
            if end != -1:
                flag = result[idx:end+1]
                print(f"!!! FLAG FOUND in {field} modulo !!!")
                print(f"FLAG: {flag}")
                return flag
    
    # Method: Look at the binary representation
    # Maybe the flag is in the mantissa/exponent of the doubles?
    for field in ['lat', 'lon', 'alt']:
        all_bytes = b''.join(struct.pack('<d', r[field]) for r in records)
        if b'Kaal{' in all_bytes:
            idx = all_bytes.index(b'Kaal{')
            end = all_bytes.find(b'}', idx)
            if end != -1:
                flag = all_bytes[idx:end+1].decode('ascii', errors='ignore')
                print(f"!!! FLAG FOUND in {field} binary representation !!!")
                print(f"FLAG: {flag}")
                return flag
    
    # Method: Check if records spell out coordinates that form letters
    # This would require plotting, which we already did
    
    # Method: Steganography - LSB of each field
    for field in ['timestamp', 'field1', 'last']:
        lsbs = [r[field] & 1 for r in records]
        # Convert bits to bytes
        byte_array = []
        for i in range(0, len(lsbs), 8):
            if i + 8 <= len(lsbs):
                byte_val = sum(lsbs[i+j] << j for j in range(8))
                byte_array.append(byte_val)
        
        lsb_bytes = bytes(byte_array)
        if b'Kaal{' in lsb_bytes:
            idx = lsb_bytes.index(b'Kaal{')
            end = lsb_bytes.find(b'}', idx)
            if end != -1:
                flag = lsb_bytes[idx:end+1].decode('ascii', errors='ignore')
                print(f"!!! FLAG FOUND in {field} LSBs !!!")
                print(f"FLAG: {flag}")
                return flag
    
    print("=== NO FLAG FOUND WITH ANY METHOD ===")
    print("\nPossible next steps:")
    print("1. The flag might be visual (drawn by the flight path)")
    print("2. Requires external tool or library specific to flight data")
    print("3. The file format is custom and requires reverse engineering the parser")
    print("4. The challenge requires additional context or files")
    
    return None

if __name__ == '__main__':
    nuclear_decode(r'D:\mission-git-hackss\flight_record.dat')
