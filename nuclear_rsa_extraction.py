#!/usr/bin/env python3
"""
Nuclear extraction - find ALL possible RSA parameters
"""

import re
import struct
import wave

def extract_everything(filename):
    """Extract every possible number and pattern"""
    print(f"\n{'='*70}")
    print(f"NUCLEAR EXTRACTION: {filename}")
    print('='*70)
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Method 1: Look for base64 encoded data
    import base64
    try:
        # Try to find base64 patterns
        text = data.decode('latin-1', errors='replace')
        # Base64 pattern
        b64_pattern = r'[A-Za-z0-9+/]{40,}={0,2}'
        b64_matches = re.findall(b64_pattern, text)
        if b64_matches:
            print(f"Found {len(b64_matches)} base64-like strings")
            for i, match in enumerate(b64_matches[:5]):
                try:
                    decoded = base64.b64decode(match)
                    if len(decoded) > 10:
                        print(f"  Decoded {i+1}: {decoded[:100]}")
                except:
                    pass
    except:
        pass
    
    # Method 2: Look for hex-encoded large numbers
    hex_pattern = r'[0-9a-fA-F]{64,}'
    hex_matches = re.findall(hex_pattern, data.hex())
    if hex_matches:
        print(f"\nFound {len(hex_matches)} long hex strings")
        for i, match in enumerate(hex_matches[:3]):
            num = int(match, 16)
            print(f"  Hex {i+1}: {num}")
            print(f"    Bit length: {num.bit_length()}")
    
    # Method 3: Extract from audio samples as big numbers
    with wave.open(filename, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        
        # Try different chunk sizes
        for chunk_size in [128, 256, 512, 1024]:
            chunk = frames[:chunk_size]
            num = int.from_bytes(chunk, 'big')
            if num.bit_length() > 512:  # RSA modulus is typically 1024+ bits
                print(f"\nAudio as number ({chunk_size} bytes):")
                print(f"  Value: {num}")
                print(f"  Bit length: {num.bit_length()}")
    
    # Method 4: Look for specific markers
    markers = [b'n=', b'c=', b'e=', b'N=', b'C=', b'E=', b'modulus', b'ciphertext']
    for marker in markers:
        if marker in data:
            idx = data.find(marker)
            context = data[idx:idx+200]
            print(f"\nFound marker {marker} at position {idx}")
            print(f"  Context: {context}")
    
    # Method 5: Check for JSON or structured data
    if b'{' in data and b'}' in data:
        try:
            import json
            # Try to find JSON
            start = data.find(b'{')
            end = data.rfind(b'}') + 1
            json_data = data[start:end].decode('utf-8', errors='ignore')
            parsed = json.loads(json_data)
            print(f"\nFound JSON data: {parsed}")
        except:
            pass

# Extract from all files
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    extract_everything(f'stones_extracted/{stone}.wav')

# Now let's try a different approach - maybe the RSA params are in the 
# relationship between the files or their properties
print("\n" + "="*70)
print("ANALYZING FILE RELATIONSHIPS")
print("="*70)

# Check if file sizes encode something
import os
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    size = os.path.getsize(filename)
    print(f"{stone}: {size} bytes")

# Maybe the challenge expects us to use an online tool or the params are on the platform
print("\n" + "="*70)
print("TRYING COMMON CTF RSA PATTERNS")
print("="*70)

# Common small RSA examples for Hastad attack
# Let me try with the numbers we found
n_from_comment = 2157869541235478521545895
secret_number = 83927465839274658392746583

print(f"Number from comment: {n_from_comment}")
print(f"  Bit length: {n_from_comment.bit_length()}")
print(f"Secret number: {secret_number}")
print(f"  Bit length: {secret_number.bit_length()}")

# These are too small for RSA moduli (need 1024+ bits typically)
# But maybe this is a toy example?

# Let me try assuming these ARE the ciphertexts and we need to find moduli
# Or maybe the audio data itself encodes the moduli

print("\n" + "="*70)
print("ATTEMPTING DIRECT AUDIO DATA AS RSA PARAMS")
print("="*70)

# Try using the first N bytes of audio as n and c
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    with wave.open(filename, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        
        # Try first 256 bytes as n, next 256 as c
        n_bytes = frames[44:44+256]  # Skip WAV header
        c_bytes = frames[44+256:44+512]
        
        n = int.from_bytes(n_bytes, 'big')
        c = int.from_bytes(c_bytes, 'big')
        
        print(f"\n{stone}:")
        print(f"  Potential n: {n}")
        print(f"  Potential c: {c}")
        print(f"  n bit length: {n.bit_length()}")
        print(f"  c bit length: {c.bit_length()}")
