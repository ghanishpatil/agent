#!/usr/bin/env python3
"""
Smart RSA solve - use what we know
The hint says "small exponent" and "repetition"
Classic Hastad attack with e=3
"""

import sys
sys.set_int_max_str_digits(100000)

# Based on typical CTF Hastad attacks, let me try to construct the attack
# with the audio data as the RSA parameters

import wave
import struct

def get_rsa_from_audio(filename):
    """Extract potential RSA params from audio data"""
    with wave.open(filename, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        
        # Skip WAV header (44 bytes)
        audio_data = frames
        
        # Try different interpretations
        # Method 1: First half as n, second half as c
        mid = len(audio_data) // 2
        
        n = int.from_bytes(audio_data[:mid], 'big')
        c = int.from_bytes(audio_data[mid:], 'big')
        
        return n, c

# Get params from all three files
params = []
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    n, c = get_rsa_from_audio(f'stones_extracted/{stone}.wav')
    params.append((c, n))
    print(f"{stone}:")
    print(f"  n bit length: {n.bit_length()}")
    print(f"  c bit length: {c.bit_length()}")

# Now perform Hastad's attack with e=3
print("\n" + "="*70)
print("PERFORMING HÅSTAD'S BROADCAST ATTACK (e=3)")
print("="*70)

c1, n1 = params[0]
c2, n2 = params[1]
c3, n3 = params[2]

# Chinese Remainder Theorem
def crt(remainders, moduli):
    total = 0
    prod = 1
    for m in moduli:
        prod *= m
    
    for r, m in zip(remainders, moduli):
        p = prod // m
        total += r * pow(p, -1, m) * p
    
    return total % prod

# Apply CRT
M_cubed = crt([c1, c2, c3], [n1, n2, n3])

print(f"M^3 calculated")

# Take cube root
def integer_cube_root(n):
    if n == 0:
        return 0
    
    # Binary search
    low = 0
    high = n
    
    while low < high:
        mid = (low + high + 1) // 2
        if mid ** 3 <= n:
            low = mid
        else:
            high = mid - 1
    
    return low

M = integer_cube_root(M_cubed)

print(f"M calculated")

# Convert to bytes
try:
    from Crypto.Util.number import long_to_bytes
    message = long_to_bytes(M)
    print(f"\nDecrypted message (first 200 bytes): {message[:200]}")
    
    # Look for flag
    if b'Kaal{' in message:
        flag_start = message.find(b'Kaal{')
        flag_end = message.find(b'}', flag_start) + 1
        flag = message[flag_start:flag_end]
        print(f"\n{'='*70}")
        print(f"FLAG FOUND: {flag.decode('utf-8')}")
        print(f"{'='*70}")
    elif b'kaal{' in message:
        flag_start = message.find(b'kaal{')
        flag_end = message.find(b'}', flag_start) + 1
        flag = message[flag_start:flag_end]
        print(f"\n{'='*70}")
        print(f"FLAG FOUND: {flag.decode('utf-8')}")
        print(f"{'='*70}")
    else:
        # Try to decode as text
        try:
            text = message.decode('utf-8', errors='ignore')
            print(f"\nAs text: {text[:500]}")
        except:
            print("\nCould not decode as text")
            
except Exception as e:
    print(f"Error: {e}")
    
    # Try alternative: maybe the numbers we found ARE the answer
    print("\n" + "="*70)
    print("TRYING WITH FOUND NUMBERS")
    print("="*70)
    
    # The secret number might be the flag or part of it
    secret = 83927465839274658392746583
    try:
        from Crypto.Util.number import long_to_bytes
        msg = long_to_bytes(secret)
        print(f"Secret as bytes: {msg}")
        print(f"Secret as text: {msg.decode('utf-8', errors='ignore')}")
    except:
        pass
