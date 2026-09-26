#!/usr/bin/env python3
"""Extract RSA parameters from the stone WAV files"""

import re

def extract_rsa_from_file(filename):
    """Extract n, c, e from file"""
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"\n{'='*60}")
    print(f"File: {filename}")
    print('='*60)
    
    # Look for patterns like n=..., c=..., e=...
    # Try to find where actual RSA params might be
    
    # Method 1: Look for text patterns
    text = data.decode('latin-1')
    
    # Search for n=, c=, e= followed by numbers
    n_match = re.search(r'n\s*=\s*(\d+)', text, re.IGNORECASE)
    c_match = re.search(r'c\s*=\s*(\d+)', text, re.IGNORECASE)
    e_match = re.search(r'e\s*=\s*(\d+)', text, re.IGNORECASE)
    
    if n_match:
        print(f"Found n = {n_match.group(1)}")
    if c_match:
        print(f"Found c = {c_match.group(1)}")
    if e_match:
        print(f"Found e = {e_match.group(1)}")
    
    # Method 2: The data might be the actual RSA values as raw bytes
    # Skip WAV header (44 bytes) and treat rest as potential RSA data
    wav_data = data[44:]  # Skip WAV header
    
    # Convert to integer
    try:
        # Try interpreting as big integer
        num = int.from_bytes(wav_data[:256], 'big')
        print(f"\nFirst 256 bytes as big-endian int:")
        print(f"  {num}")
        
        num_little = int.from_bytes(wav_data[:256], 'little')
        print(f"\nFirst 256 bytes as little-endian int:")
        print(f"  {num_little}")
    except:
        pass
    
    # Method 3: Look for very long number strings
    numbers = re.findall(r'\d{50,}', text)
    if numbers:
        print(f"\nFound long numbers:")
        for num in numbers[:5]:
            print(f"  {num[:100]}...")
    
    return None

# Extract from all three files
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    extract_rsa_from_file(f'stones_extracted/{stone}.wav')

# Let's also try a different approach - maybe the files contain the params in metadata
print("\n" + "="*60)
print("Checking for metadata/comments in WAV files")
print("="*60)

import wave

for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    with wave.open(filename, 'rb') as wav:
        # Check if there's any metadata
        print(f"\n{stone}:")
        print(f"  Params: {wav.getparams()}")
        
        # Read raw file to check for RIFF chunks
        with open(filename, 'rb') as f:
            raw = f.read()
            
            # Look for common metadata chunks
            if b'INFO' in raw:
                idx = raw.find(b'INFO')
                print(f"  Found INFO chunk at {idx}")
                print(f"  Data: {raw[idx:idx+200]}")
            
            if b'LIST' in raw:
                idx = raw.find(b'LIST')
                print(f"  Found LIST chunk at {idx}")
                print(f"  Data: {raw[idx:idx+200]}")
