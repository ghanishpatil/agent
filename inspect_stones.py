#!/usr/bin/env python3
"""Inspect the stone WAV files for embedded RSA data"""

import wave
import struct

def inspect_wav(filename):
    """Inspect WAV file structure and content"""
    print(f"\n{'='*60}")
    print(f"Inspecting: {filename}")
    print('='*60)
    
    with wave.open(filename, 'rb') as wav:
        print(f"Channels: {wav.getnchannels()}")
        print(f"Sample Width: {wav.getsampwidth()} bytes")
        print(f"Frame Rate: {wav.getframerate()} Hz")
        print(f"Frames: {wav.getnframes()}")
        print(f"Compression: {wav.getcomptype()}")
        
        # Read all frames
        frames = wav.readframes(wav.getnframes())
        print(f"Total bytes: {len(frames)}")
        
        # Try to decode as ASCII/UTF-8
        try:
            text = frames.decode('ascii', errors='ignore')
            # Look for RSA parameters
            if 'n' in text or 'c' in text or 'e' in text or '=' in text:
                print("\nFound potential text data:")
                # Print readable parts
                readable = ''.join(c if c.isprintable() else ' ' for c in text)
                print(readable[:1000])
        except:
            pass
        
        # Check for hex patterns
        hex_str = frames.hex()
        print(f"\nFirst 200 hex bytes: {hex_str[:400]}")
        
        # Look for common patterns
        if b'n=' in frames or b'c=' in frames or b'e=' in frames:
            print("\nFound RSA parameter markers!")
            idx = frames.find(b'n=')
            if idx != -1:
                print(f"Data around 'n=': {frames[idx:idx+200]}")
        
        # Check if it's actually audio or data
        samples = struct.unpack(f'{len(frames)//2}h', frames)
        avg = sum(abs(s) for s in samples[:100]) / 100
        print(f"\nAverage sample magnitude: {avg:.2f}")
        if avg < 100:
            print("This looks like data, not audio!")

# Inspect all three files
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    inspect_wav(f'stones_extracted/{stone}.wav')

# Also check with strings command approach
print("\n" + "="*60)
print("Searching for printable strings...")
print("="*60)

for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    with open(filename, 'rb') as f:
        data = f.read()
        
        # Extract strings (sequences of printable chars)
        current_string = []
        strings = []
        
        for byte in data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_string.append(chr(byte))
            else:
                if len(current_string) >= 4:
                    strings.append(''.join(current_string))
                current_string = []
        
        if current_string and len(current_string) >= 4:
            strings.append(''.join(current_string))
        
        print(f"\n{stone}:")
        # Look for interesting strings
        for s in strings:
            if any(keyword in s.lower() for keyword in ['flag', 'kaal', 'n=', 'c=', 'e=', 'rsa']):
                print(f"  {s}")
            elif len(s) > 50:  # Long strings might be base64 or hex
                print(f"  {s[:100]}...")
