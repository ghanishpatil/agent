#!/usr/bin/env python3
"""Extract the hidden ZIP file from mind_stone"""

import struct

# Read the mind_stone file
with open('stones_extracted/mind_stone_3rd.wav', 'rb') as f:
    # Read RIFF header to find where WAV ends
    riff = f.read(4)
    file_size = struct.unpack('<I', f.read(4))[0]
    
    # Skip to end of WAV data
    f.seek(file_size + 8)
    
    # Read the extra data
    extra_data = f.read()
    
    print(f"Found {len(extra_data)} bytes of extra data")
    
    # The first line is the number, then comes the ZIP
    lines = extra_data.split(b'\n', 1)
    number = lines[0].decode('ascii').strip()
    zip_data = lines[1] if len(lines) > 1 else b''
    
    print(f"Number: {number}")
    print(f"ZIP data size: {len(zip_data)} bytes")
    
    # Save the ZIP file
    with open('hidden_secret.zip', 'wb') as zf:
        zf.write(zip_data)
    
    print("Saved to: hidden_secret.zip")

# Try to extract the ZIP
import zipfile

try:
    with zipfile.ZipFile('hidden_secret.zip', 'r') as zf:
        print(f"\nZIP contents: {zf.namelist()}")
        
        # Try to extract (might be password protected)
        try:
            zf.extractall('hidden_extracted')
            print("Extracted successfully to: hidden_extracted/")
            
            # Read the secret.txt
            with open('hidden_extracted/secret.txt', 'r') as f:
                content = f.read()
                print(f"\nsecret.txt content:")
                print(content)
        except RuntimeError as e:
            if 'password' in str(e).lower():
                print("\n*** ZIP is password protected! ***")
                print(f"Password might be: {number}")
                
                # Try with the number as password
                try:
                    zf.extractall('hidden_extracted', pwd=number.encode())
                    print(f"Extracted with password: {number}")
                    
                    with open('hidden_extracted/secret.txt', 'r') as f:
                        content = f.read()
                        print(f"\nsecret.txt content:")
                        print(content)
                except:
                    print("Password didn't work")
            else:
                print(f"Error: {e}")
except Exception as e:
    print(f"Error opening ZIP: {e}")
