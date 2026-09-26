#!/usr/bin/env python3
"""
Try to parse as a filesystem or boot sector
55AA is the boot sector signature
"""

import struct

def parse_boot_sector(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    print("=== Boot Sector / MBR Analysis ===\n")
    
    # Check if it's a standard MBR
    if len(data) < 512:
        print("File too small for MBR")
        return
    
    # MBR structure (simplified):
    # 0-445: Bootstrap code
    # 446-509: Partition table (4 entries of 16 bytes each)
    # 510-511: Boot signature (0x55AA)
    
    boot_sig = struct.unpack('<H', data[510:512])[0]
    print(f"Boot signature at 510-511: 0x{boot_sig:04x}")
    
    if boot_sig == 0xAA55:
        print("Valid boot signature found!")
    
    # But our file starts with 55AA55AA, which is unusual
    # Let's check if there's a partition table
    print("\n=== Partition Table (if present) ===")
    for i in range(4):
        offset = 446 + i * 16
        if offset + 16 <= len(data):
            entry = data[offset:offset+16]
            
            status = entry[0]
            part_type = entry[4]
            lba_start = struct.unpack('<I', entry[8:12])[0]
            num_sectors = struct.unpack('<I', entry[12:16])[0]
            
            if part_type != 0:
                print(f"\nPartition {i+1}:")
                print(f"  Status: 0x{status:02x}")
                print(f"  Type: 0x{part_type:02x}")
                print(f"  LBA Start: {lba_start}")
                print(f"  Sectors: {num_sectors}")
                print(f"  Size: {num_sectors * 512} bytes")
    
    # Try to find FAT filesystem
    print("\n=== Checking for FAT filesystem ===")
    # FAT boot sector has specific fields
    if len(data) >= 512:
        oem_name = data[3:11]
        bytes_per_sector = struct.unpack('<H', data[11:13])[0]
        sectors_per_cluster = data[13]
        reserved_sectors = struct.unpack('<H', data[14:16])[0]
        num_fats = data[16]
        
        print(f"OEM Name: {oem_name}")
        print(f"Bytes per sector: {bytes_per_sector}")
        print(f"Sectors per cluster: {sectors_per_cluster}")
        print(f"Reserved sectors: {reserved_sectors}")
        print(f"Number of FATs: {num_fats}")
    
    # Maybe the actual data starts after a header?
    # Let's check different offsets
    print("\n=== Checking for data at different offsets ===")
    for offset in [0, 256, 512, 1024, 2048]:
        if offset + 100 < len(data):
            chunk = data[offset:offset+100]
            # Check for ASCII strings
            ascii_count = sum(1 for b in chunk if 32 <= b < 127)
            if ascii_count > 50:
                print(f"\nHigh ASCII content at offset {offset}:")
                print(''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk))
            
            # Check for flag
            if b'Kaal{' in chunk:
                print(f"\nFLAG FOUND at offset {offset}!")
                print(chunk)
    
    # Try to extract files if this is a filesystem
    print("\n=== Looking for file signatures ===")
    # Common file signatures
    sigs = {
        b'PK\x03\x04': ('ZIP', 0),
        b'\x1f\x8b\x08': ('GZIP', 0),
        b'%PDF': ('PDF', 0),
        b'\x89PNG': ('PNG', 0),
        b'GIF8': ('GIF', 0),
        b'\xff\xd8\xff': ('JPEG', 0),
        b'BM': ('BMP', 0),
        b'MZ': ('EXE', 0),
        b'\x7fELF': ('ELF', 0),
        b'Rar!': ('RAR', 0),
    }
    
    for sig, (name, _) in sigs.items():
        idx = 0
        count = 0
        while True:
            idx = data.find(sig, idx)
            if idx == -1:
                break
            count += 1
            if count <= 3:  # Only show first 3 occurrences
                print(f"{name} at offset {idx}")
            idx += 1
        if count > 3:
            print(f"  ... and {count - 3} more")
    
    # Check if the coordinates themselves encode something
    print("\n=== Trying to decode coordinates as characters ===")
    offset = 256
    decoded_chars = []
    
    for _ in range(100):
        if offset + 40 > len(data):
            break
        
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            # Try different fields
            # Field at offset 8-11
            field = struct.unpack('<I', data[offset+8:offset+12])[0]
            
            # Try to extract ASCII
            for i in range(4):
                byte = (field >> (i*8)) & 0xFF
                if 32 <= byte < 127:
                    decoded_chars.append(chr(byte))
            
            offset += 40
    
    decoded_str = ''.join(decoded_chars)
    print(f"Decoded from field 8-11: {decoded_str[:200]}")
    
    if 'Kaal{' in decoded_str:
        idx = decoded_str.index('Kaal{')
        print(f"\nFLAG: {decoded_str[idx:idx+100]}")

if __name__ == '__main__':
    parse_boot_sector(r'D:\mission-git-hackss\flight_record.dat')
