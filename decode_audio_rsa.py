#!/usr/bin/env python3
"""
Decode RSA parameters from audio samples
The hint mentions 'repetition was intentional' - maybe the audio encodes data through LSB or patterns
"""

import wave
import struct

def extract_lsb_from_audio(filename):
    """Extract LSB from audio samples"""
    with wave.open(filename, 'rb') as wav:
        n_frames = wav.getnframes()
        frames = wav.readframes(n_frames)
        
        # Unpack as 16-bit signed integers
        samples = struct.unpack(f'<{n_frames}h', frames)
        
        # Extract LSB from each sample
        lsb_bits = [s & 1 for s in samples]
        
        # Convert bits to bytes
        lsb_bytes = bytearray()
        for i in range(0, len(lsb_bits), 8):
            if i + 8 <= len(lsb_bits):
                byte = 0
                for j in range(8):
                    byte |= (lsb_bits[i + j] << j)
                lsb_bytes.append(byte)
        
        return bytes(lsb_bytes)

def find_rsa_in_data(data, filename):
    """Search for RSA parameters in extracted data"""
    print(f"\n{'='*60}")
    print(f"Analyzing LSB data from: {filename}")
    print('='*60)
    
    # Try to decode as text
    try:
        text = data.decode('ascii', errors='ignore')
        print(f"First 500 chars: {text[:500]}")
        
        # Look for n=, c=, e= patterns
        import re
        n_match = re.search(r'n\s*=\s*(\d+)', text)
        c_match = re.search(r'c\s*=\s*(\d+)', text)
        e_match = re.search(r'e\s*=\s*(\d+)', text)
        
        result = {}
        if n_match:
            result['n'] = int(n_match.group(1))
            print(f"\nFound n = {result['n']}")
        if c_match:
            result['c'] = int(c_match.group(1))
            print(f"Found c = {result['c']}")
        if e_match:
            result['e'] = int(e_match.group(1))
            print(f"Found e = {result['e']}")
        
        return result
    except:
        print("Could not decode as ASCII")
        return {}

# Extract LSB from all three files
print("Extracting LSB steganography from audio files...")

stones_data = {}
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    lsb_data = extract_lsb_from_audio(filename)
    stones_data[stone] = find_rsa_in_data(lsb_data, stone)

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
for stone, params in stones_data.items():
    print(f"\n{stone}:")
    for key, value in params.items():
        if key in ['n', 'c']:
            print(f"  {key} = {value}")
            print(f"  {key} bit length = {value.bit_length()}")
        else:
            print(f"  {key} = {value}")

# If we have all parameters, attempt Håstad's attack
if all(stones_data.values()):
    print("\n" + "="*60)
    print("ATTEMPTING HÅSTAD'S BROADCAST ATTACK")
    print("="*60)
    
    # Check if we have e=3 for all (or same small e)
    exponents = [params.get('e') for params in stones_data.values() if 'e' in params]
    print(f"Exponents found: {exponents}")
    
    if len(exponents) == 3 and len(set(exponents)) == 1:
        e = exponents[0]
        print(f"\nAll files use e = {e}")
        
        # Extract n and c for each
        params_list = []
        for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
            if 'n' in stones_data[stone] and 'c' in stones_data[stone]:
                params_list.append((stones_data[stone]['c'], stones_data[stone]['n']))
        
        if len(params_list) == 3:
            print("\nHave all 3 (c, n) pairs - ready for attack!")
            
            # Perform CRT + cube root
            c1, n1 = params_list[0]
            c2, n2 = params_list[1]
            c3, n3 = params_list[2]
            
            print(f"\nc1 = {c1}")
            print(f"n1 = {n1}")
            print(f"\nc2 = {c2}")
            print(f"n2 = {n2}")
            print(f"\nc3 = {c3}")
            print(f"n3 = {n3}")
