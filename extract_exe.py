#!/usr/bin/env python3
"""
Extract the embedded EXE file from flight_record.dat
"""

import struct

def extract_exe(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Find MZ signature
    mz_offset = data.find(b'MZ')
    
    if mz_offset == -1:
        print("No MZ signature found")
        return
    
    print(f"MZ signature found at offset: {mz_offset}")
    
    # MZ header structure (simplified):
    # 0-1: "MZ"
    # 2-3: Bytes on last page
    # 4-5: Pages in file
    # ...
    # 60-63: PE header offset (for PE files)
    
    # For DOS executables, we need to find the end
    # For PE files, there's a PE header
    
    # Check if it's a PE file
    if mz_offset + 64 <= len(data):
        pe_offset_pos = mz_offset + 60
        pe_offset = struct.unpack('<I', data[pe_offset_pos:pe_offset_pos+4])[0]
        print(f"PE header offset: {pe_offset}")
        
        if mz_offset + pe_offset + 4 <= len(data):
            pe_sig = data[mz_offset + pe_offset:mz_offset + pe_offset + 4]
            print(f"PE signature: {pe_sig}")
            
            if pe_sig == b'PE\x00\x00':
                print("This is a PE executable")
    
    # Try to determine file size
    # Look for the next record marker after the MZ
    next_marker = data.find(b'\x01\x55\x24\x00', mz_offset + 100)
    
    if next_marker != -1:
        exe_size = next_marker - mz_offset
        print(f"Estimated EXE size: {exe_size} bytes (until next record marker)")
    else:
        # Extract until end of file
        exe_size = len(data) - mz_offset
        print(f"Extracting until end of file: {exe_size} bytes")
    
    # Extract the EXE
    exe_data = data[mz_offset:mz_offset + exe_size]
    
    with open('extracted.exe', 'wb') as f:
        f.write(exe_data)
    
    print(f"Extracted EXE to extracted.exe ({len(exe_data)} bytes)")
    
    # Try to analyze it
    print("\n=== EXE Analysis ===")
    print(f"First 200 bytes (hex):")
    for i in range(0, min(200, len(exe_data)), 16):
        hex_str = ' '.join(f'{b:02x}' for b in exe_data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in exe_data[i:i+16])
        print(f'{i:08x}  {hex_str:<48}  {ascii_str}')
    
    # Search for strings in the EXE
    print("\n=== Strings in EXE ===")
    strings = []
    current = []
    for byte in exe_data:
        if 32 <= byte < 127:
            current.append(chr(byte))
        else:
            if len(current) >= 4:
                strings.append(''.join(current))
            current = []
    if current and len(current) >= 4:
        strings.append(''.join(current))
    
    for s in strings[:50]:
        print(f"  {s}")
        if 'Kaal{' in s or 'flag' in s.lower():
            print(f"  ^^^ POTENTIAL FLAG ^^^")
    
    # Check if flag is in the EXE
    if b'Kaal{' in exe_data:
        idx = exe_data.index(b'Kaal{')
        print(f"\n!!! FLAG FOUND in EXE at offset {idx} !!!")
        print(exe_data[idx:idx+100])

if __name__ == '__main__':
    extract_exe(r'D:\mission-git-hackss\flight_record.dat')
