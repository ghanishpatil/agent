#!/usr/bin/env python3
"""
Find data appended after the audio ends
"""

import struct
import re

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

print("[*] Analyzing file structure...")
print(f"    Total file size: {len(data)} bytes")

# Parse RIFF/WAV structure
if data[:4] == b'RIFX' or data[:4] == b'RIFF':
    print(f"    File type: {data[:4].decode()}")
    
    # Get declared size
    declared_size = struct.unpack('<I', data[4:8])[0]
    print(f"    Declared RIFF size: {declared_size} bytes")
    print(f"    Actual file size: {len(data)} bytes")
    
    # Calculate where RIFF should end
    riff_end = 8 + declared_size
    print(f"    RIFF should end at: {riff_end}")
    
    if riff_end < len(data):
        appended_size = len(data) - riff_end
        print(f"\n[+] APPENDED DATA FOUND: {appended_size} bytes after RIFF end!")
        
        appended_data = data[riff_end:]
        print(f"\n    First 500 bytes of appended data:")
        print(appended_data[:500])
        
        print(f"\n    Hex:")
        print(appended_data[:200].hex())
        
        # Check for file signatures
        print(f"\n    Checking for file signatures...")
        if appended_data[:2] == b'PK':
            print("    [+] ZIP file!")
        elif appended_data[:4] == b'\x89PNG':
            print("    [+] PNG image!")
        elif appended_data[:2] == b'\xff\xd8':
            print("    [+] JPEG image!")
        elif appended_data[:4] == b'%PDF':
            print("    [+] PDF file!")
        
        # Look for flag
        flags = re.findall(rb'Kaal\{[^}]+\}', appended_data)
        if flags:
            print(f"\n[+] FLAGS IN APPENDED DATA:")
            for flag in flags:
                print(f"    {flag.decode('utf-8', errors='ignore')}")
        
        # Save appended data
        with open('appended_data.bin', 'wb') as f:
            f.write(appended_data)
        print(f"\n    Saved to appended_data.bin")
        
        # Try to extract as text
        try:
            text = appended_data.decode('utf-8', errors='ignore')
            if len(text) > 10:
                print(f"\n    As text:")
                print(text[:500])
        except:
            pass

# Also check the data chunk size vs actual data
data_pos = data.find(b'data')
if data_pos != -1:
    data_chunk_size = struct.unpack('<I', data[data_pos+4:data_pos+8])[0]
    print(f"\n[*] Data chunk analysis:")
    print(f"    Data chunk declared size: {data_chunk_size} bytes")
    print(f"    Data chunk starts at: {data_pos + 8}")
    print(f"    Data chunk should end at: {data_pos + 8 + data_chunk_size}")
    
    data_chunk_end = data_pos + 8 + data_chunk_size
    
    if data_chunk_end < len(data):
        after_data = len(data) - data_chunk_end
        print(f"    [+] {after_data} bytes after data chunk!")
        
        trailing_data = data[data_chunk_end:]
        print(f"\n    Trailing data:")
        print(trailing_data)
        
        # Look for flag
        flags = re.findall(rb'Kaal\{[^}]+\}', trailing_data)
        if flags:
            print(f"\n[+] *** FLAGS IN TRAILING DATA ***:")
            for flag in flags:
                decoded_flag = flag.decode('utf-8', errors='ignore')
                print(f"    {decoded_flag}")
                if decoded_flag != 'Kaal{1_th1nk_th15_15_wr0ng}':
                    print(f"    ^^^ THIS IS DIFFERENT FROM THE FAKE FLAG!")

print("\n[*] Analysis complete!")
