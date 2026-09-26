#!/usr/bin/env python3
"""
Extract the ZIP file from the data
"""

import struct
import zipfile
import io

def extract_zip(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Find all PK signatures
    print("=== Searching for ZIP signatures ===")
    idx = 0
    zip_offsets = []
    
    while True:
        idx = data.find(b'PK', idx)
        if idx == -1:
            break
        
        # Check what type of PK signature
        if idx + 4 <= len(data):
            sig = data[idx:idx+4]
            if sig == b'PK\x03\x04':
                print(f"Local file header at offset {idx}")
                zip_offsets.append(idx)
            elif sig == b'PK\x01\x02':
                print(f"Central directory at offset {idx}")
            elif sig == b'PK\x05\x06':
                print(f"End of central directory at offset {idx}")
        
        idx += 1
    
    if not zip_offsets:
        print("No ZIP local file headers found")
        return
    
    # Try to extract from each offset
    for zip_offset in zip_offsets:
        print(f"\n=== Trying to extract ZIP from offset {zip_offset} ===")
        
        # Try different lengths
        for length in [1000, 5000, 10000, 50000, len(data) - zip_offset]:
            try:
                zip_data = data[zip_offset:zip_offset + length]
                
                # Try to open as ZIP
                with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                    print(f"  Successfully opened ZIP with length {length}")
                    print(f"  Files in ZIP: {zf.namelist()}")
                    
                    # Extract all files
                    for name in zf.namelist():
                        content = zf.read(name)
                        print(f"\n  File: {name}")
                        print(f"  Size: {len(content)} bytes")
                        
                        # Check if it contains the flag
                        if b'Kaal{' in content:
                            idx = content.index(b'Kaal{')
                            end = content.find(b'}', idx)
                            if end != -1:
                                print(f"\n  !!! FLAG FOUND !!!")
                                print(f"  FLAG: {content[idx:end+1].decode('ascii', errors='ignore')}")
                                return
                        
                        # Print content if it's text
                        if len(content) < 10000:
                            try:
                                text = content.decode('ascii', errors='ignore')
                                print(f"  Content: {text[:500]}")
                            except:
                                print(f"  Content (hex): {content[:200].hex()}")
                    
                    break  # Successfully extracted
            except zipfile.BadZipFile:
                continue
            except Exception as e:
                if length == len(data) - zip_offset:
                    print(f"  Failed to extract: {e}")
                continue

if __name__ == '__main__':
    extract_zip(r'D:\mission-git-hackss\flight_record.dat')
