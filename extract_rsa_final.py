#!/usr/bin/env python3
"""
Extract RSA parameters - they might be in plaintext somewhere in the file
"""

import re

def extract_params_carefully(filename):
    """Extract n, c, e from file"""
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"\n{'='*70}")
    print(f"File: {filename}")
    print('='*70)
    
    # Search for patterns in hex
    hex_str = data.hex()
    
    # Look for "n=" in hex (6e3d)
    # Look for "c=" in hex (633d)
    # Look for "e=" in hex (653d)
    
    # Method: Find these markers and extract the number after them
    # Numbers might be in ASCII decimal or hex
    
    # Convert to string for easier searching
    text = data.decode('latin-1', errors='replace')
    
    # Find all instances of e=, n=, c= followed by digits
    e_pattern = r'e\s*=\s*(\d+)'
    n_pattern = r'n\s*=\s*(\d{50,})'  # n should be a large number
    c_pattern = r'c\s*=\s*(\d{50,})'  # c should be a large number
    
    e_matches = re.findall(e_pattern, text, re.IGNORECASE)
    n_matches = re.findall(n_pattern, text, re.IGNORECASE)
    c_matches = re.findall(c_pattern, text, re.IGNORECASE)
    
    print(f"e matches: {e_matches}")
    print(f"n matches (count): {len(n_matches)}")
    print(f"c matches (count): {len(c_matches)}")
    
    if n_matches:
        print(f"\nFirst n: {n_matches[0][:100]}...")
    if c_matches:
        print(f"First c: {c_matches[0][:100]}...")
    
    # Also check for the pattern in the filename itself or metadata
    # The comment in mind_stone had a number
    if b'ICMT' in data:
        idx = data.find(b'ICMT')
        import struct
        chunk_size = struct.unpack('<I', data[idx+4:idx+8])[0]
        comment = data[idx+8:idx+8+chunk_size].decode('ascii', errors='ignore').strip('\x00')
        print(f"\nICMT comment: {comment}")
    
    return {
        'e': e_matches,
        'n': n_matches,
        'c': c_matches
    }

# Extract from all files
results = {}
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    results[stone] = extract_params_carefully(f'stones_extracted/{stone}.wav')

# Try another approach: maybe the RSA params are the audio samples themselves
print("\n" + "="*70)
print("ALTERNATIVE: Treating audio data as RSA parameters")
print("="*70)

import wave
import struct

for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    with wave.open(filename, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        
        # Try interpreting the raw audio data as a big integer
        # Take first N bytes and convert
        test_bytes = frames[:512]  # Try first 512 bytes
        
        num_big = int.from_bytes(test_bytes, 'big')
        num_little = int.from_bytes(test_bytes, 'little')
        
        print(f"\n{stone}:")
        print(f"  As big-endian (512 bytes): {num_big}")
        print(f"  Bit length: {num_big.bit_length()}")
        print(f"  As little-endian (512 bytes): {num_little}")
        print(f"  Bit length: {num_little.bit_length()}")
