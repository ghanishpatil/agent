#!/usr/bin/env python3
"""
Try different decoding approaches for flight_record.dat
The coordinates, timestamps, or other fields might encode the flag
"""

import struct

def extract_all_fields(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    records = []
    offset = 256
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            try:
                # Parse record structure
                marker = struct.unpack('<H', data[offset:offset+2])[0]
                rec_type = struct.unpack('<H', data[offset+2:offset+4])[0]
                timestamp = struct.unpack('<I', data[offset+4:offset+8])[0]
                field1 = struct.unpack('<I', data[offset+8:offset+12])[0]
                
                # Three doubles
                val1 = struct.unpack('<d', data[offset+12:offset+20])[0]
                val2 = struct.unpack('<d', data[offset+20:offset+28])[0]
                val3 = struct.unpack('<d', data[offset+28:offset+36])[0]
                
                # Last 4 bytes
                last_field = struct.unpack('<I', data[offset+36:offset+40])[0]
                
                records.append({
                    'marker': marker,
                    'type': rec_type,
                    'timestamp': timestamp,
                    'field1': field1,
                    'val1': val1,
                    'val2': val2,
                    'val3': val3,
                    'last': last_field
                })
                
                offset += 40
            except:
                offset += 1
        else:
            offset += 1
    
    return records

def try_decode_methods(records):
    print(f"Total records: {len(records)}")
    
    # Method 1: Check if type field encodes ASCII
    print("\n=== Method 1: Type field as ASCII ===")
    type_chars = []
    for r in records[:100]:
        t = r['type']
        if t < 256:
            type_chars.append(chr(t) if 32 <= t < 127 else '.')
    print(''.join(type_chars))
    
    # Method 2: Check timestamp differences
    print("\n=== Method 2: Timestamp analysis ===")
    timestamps = [r['timestamp'] for r in records]
    diffs = [timestamps[i+1] - timestamps[i] for i in range(min(20, len(timestamps)-1))]
    print(f"First 20 timestamp differences: {diffs}")
    
    # Method 3: Check field1 (the mysterious field)
    print("\n=== Method 3: Field1 analysis ===")
    field1_values = [r['field1'] for r in records if r['field1'] != 0]
    print(f"Non-zero field1 values (first 20): {field1_values[:20]}")
    
    # Try to interpret as ASCII
    field1_chars = []
    for r in records:
        f = r['field1']
        if f < 256 and 32 <= f < 127:
            field1_chars.append(chr(f))
        elif f == 0:
            pass  # Skip zeros
        else:
            # Try each byte
            for i in range(4):
                byte = (f >> (i*8)) & 0xFF
                if 32 <= byte < 127:
                    field1_chars.append(chr(byte))
    
    print(f"Field1 as ASCII: {''.join(field1_chars[:200])}")
    
    # Method 4: Look at the doubles more carefully
    print("\n=== Method 4: Double values analysis ===")
    # Check if any doubles are actually integers
    for i, r in enumerate(records[:10]):
        v1_int = int(r['val1'])
        v2_int = int(r['val2'])
        v3_int = int(r['val3'])
        
        print(f"Record {i+1}:")
        print(f"  val1: {r['val1']:.10f} -> int: {v1_int}")
        print(f"  val2: {r['val2']:.10f} -> int: {v2_int}")
        print(f"  val3: {r['val3']:.10f} -> int: {v3_int}")
        
        # Try to interpret as bytes
        v1_bytes = struct.pack('<d', r['val1'])
        v2_bytes = struct.pack('<d', r['val2'])
        v3_bytes = struct.pack('<d', r['val3'])
        
        print(f"  val1 bytes: {v1_bytes.hex()}")
        print(f"  val2 bytes: {v2_bytes.hex()}")
        print(f"  val3 bytes: {v3_bytes.hex()}")
    
    # Method 5: Extract all bytes from specific positions
    print("\n=== Method 5: Extracting bytes from position 36-39 ===")
    last_field_values = [r['last'] for r in records[:50]]
    print(f"First 50 'last' field values: {last_field_values}")
    
    # Try as ASCII
    last_chars = []
    for val in last_field_values:
        for i in range(4):
            byte = (val >> (i*8)) & 0xFF
            if 32 <= byte < 127:
                last_chars.append(chr(byte))
    print(f"Last field as ASCII: {''.join(last_chars)}")
    
    # Method 6: Look for patterns in the raw bytes
    print("\n=== Method 6: Check for hidden message in record bytes ===")
    # Extract specific byte positions from each record
    for byte_pos in [0, 1, 2, 3, 36, 37, 38, 39]:
        print(f"\nByte position {byte_pos}:")
        with open(r'D:\mission-git-hackss\flight_record.dat', 'rb') as f:
            data = f.read()
        
        bytes_at_pos = []
        offset = 256
        count = 0
        while offset < len(data) - 40 and count < 100:
            if data[offset] == 0x01 and data[offset+1] == 0x55:
                bytes_at_pos.append(data[offset + byte_pos])
                offset += 40
                count += 1
            else:
                offset += 1
        
        # Try as ASCII
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in bytes_at_pos)
        print(f"  First 100 records: {ascii_str}")

if __name__ == '__main__':
    records = extract_all_fields(r'D:\mission-git-hackss\flight_record.dat')
    try_decode_methods(records)
