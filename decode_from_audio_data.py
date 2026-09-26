#!/usr/bin/env python3
"""
CRITICAL INSIGHT: Maybe the RSA ciphertext IS the audio data itself!
The audio samples, when interpreted as a large number, ARE the ciphertext!
"""

import wave
import struct
from Crypto.Util.number import long_to_bytes
import sys
sys.set_int_max_str_digits(100000)

print("="*70)
print("HYPOTHESIS: Audio samples ARE the RSA ciphertexts")
print("="*70)

# Extract audio data from each file and treat as large integers
ciphertexts = []
moduli = []

for i, stone in enumerate(['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd'], 1):
    filename = f'stones_extracted/{stone}.wav'
    
    print(f"\n{stone}:")
    
    with wave.open(filename, 'rb') as wav:
        n_frames = wav.getnframes()
        frames = wav.readframes(n_frames)
        
        print(f"  Audio frames: {n_frames}")
        print(f"  Audio bytes: {len(frames)}")
        
        # Convert audio data to integer (this could be the ciphertext!)
        c = int.from_bytes(frames, 'big')
        print(f"  As integer bit length: {c.bit_length()}")
        
        ciphertexts.append(c)

# Now we have three ciphertexts
# But we still need the moduli (n values)
# WAIT - maybe the numbers we found ARE related to the moduli!

print("\n" + "="*70)
print("CRITICAL REALIZATION")
print("="*70)
print("We have:")
print(f"  Number from comment: 2157869541235478521545895")
print(f"  Secret number: 83927465839274658392746583")
print("\nMaybe these ARE n and c for one of the encryptions?")
print("Or maybe they're HINTS to derive the actual values?")

# Let's try: what if the secret number IS the plaintext message M?
# And we need to verify it by checking if M^3 mod n equals one of our ciphertexts?

M = 83927465839274658392746583
n_candidate = 2157869541235478521545895

print(f"\nTesting if secret is the plaintext:")
print(f"M = {M}")
print(f"M^3 = {M**3}")

# This is too small to be useful for RSA...

# ALTERNATIVE: Maybe the file NAMES or METADATA encode the moduli?
print("\n" + "="*70)
print("Checking file properties for patterns")
print("="*70)

for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    
    with wave.open(filename, 'rb') as wav:
        print(f"\n{stone}:")
        print(f"  Frames: {wav.getnframes()}")
        print(f"  Sample rate: {wav.getframerate()}")
        print(f"  Duration: {wav.getnframes() / wav.getframerate():.10f} seconds")
        
        # Maybe the frame count or duration encodes something?
        frames = wav.getnframes()
        
        # Try using frame count as part of the key
        print(f"  Frame count could be part of n or c")

# Let me try a DIFFERENT approach based on the hint
print("\n" + "="*70)
print("RE-READING THE HINT CAREFULLY")
print("="*70)
print("'Three fragments. Same pattern. Repetition was intentional.'")
print("'When the exponent is small, the message doesn't stay hidden for long.'")
print("\nThis DEFINITELY means Håstad with e=3")
print("But WHERE are n1, n2, n3 and c1, c2, c3?")
print("\nMaybe I need to look at the FREQUENCY or PHASE of the audio?")
print("Or maybe there's a PATTERN in how the data repeats?")

# Check if audio data has repeating patterns
print("\n" + "="*70)
print("Checking for repeating patterns in audio")
print("="*70)

for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    
    with wave.open(filename, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        
        # Check if there are repeating chunks
        chunk_size = 1000
        first_chunk = frames[:chunk_size]
        
        # Count how many times this chunk repeats
        count = frames.count(first_chunk)
        
        print(f"\n{stone}:")
        print(f"  First {chunk_size} bytes repeat {count} times")
        
        if count > 1:
            print(f"  *** REPETITION FOUND! ***")
