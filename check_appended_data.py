#!/usr/bin/env python3
"""
Check if there's data appended after the WAV audio data
"""

import struct

def check_wav_for_extra_data(filename):
    """Check if there's extra data after the WAV file ends"""
    print(f"\n{'='*60}")
    print(f"Checking: {filename}")
    print('='*60)
    
    with open(filename, 'rb') as f:
        # Read RIFF header
        riff = f.read(4)
        if riff != b'RIFF':
            print("Not a RIFF file!")
            return
        
        file_size = struct.unpack('<I', f.read(4))[0]
        print(f"RIFF chunk size: {file_size}")
        print(f"Expected file size: {file_size + 8} bytes")
        
        # Get actual file size
        f.seek(0, 2)  # Seek to end
        actual_size = f.tell()
        print(f"Actual file size: {actual_size} bytes")
        
        if actual_size > file_size + 8:
            extra_bytes = actual_size - (file_size + 8)
            print(f"\n*** EXTRA DATA FOUND: {extra_bytes} bytes ***")
            
            # Read the extra data
            f.seek(file_size + 8)
            extra_data = f.read()
            
            print(f"\nExtra data (first 500 bytes):")
            print(extra_data[:500])
            
            # Try to decode as text
            try:
                text = extra_data.decode('ascii', errors='ignore')
                print(f"\nAs text:")
                print(text[:1000])
                
                # Look for RSA parameters
                import re
                n_match = re.search(r'n\s*=\s*(\d+)', text)
                c_match = re.search(r'c\s*=\s*(\d+)', text)
                e_match = re.search(r'e\s*=\s*(\d+)', text)
                
                if n_match or c_match or e_match:
                    print("\n*** RSA PARAMETERS FOUND ***")
                    if n_match:
                        print(f"n = {n_match.group(1)}")
                    if c_match:
                        print(f"c = {c_match.group(1)}")
                    if e_match:
                        print(f"e = {e_match.group(1)}")
                    
                    return {
                        'n': int(n_match.group(1)) if n_match else None,
                        'c': int(c_match.group(1)) if c_match else None,
                        'e': int(e_match.group(1)) if e_match else None
                    }
            except:
                pass
        else:
            print("No extra data found")
    
    return None

# Check all three files
results = {}
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    result = check_wav_for_extra_data(f'stones_extracted/{stone}.wav')
    if result:
        results[stone] = result

if results:
    print("\n" + "="*60)
    print("SUMMARY OF RSA PARAMETERS")
    print("="*60)
    for stone, params in results.items():
        print(f"\n{stone}:")
        for key, value in params.items():
            if value:
                print(f"  {key} = {value}")
