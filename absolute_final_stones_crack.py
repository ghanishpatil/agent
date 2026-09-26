#!/usr/bin/env python3
"""
ABSOLUTE FINAL ATTEMPT - Try EVERYTHING
Maybe the n and c are encoded in the audio frequency, duration, or sample patterns
"""

import wave
import struct
from Crypto.Util.number import long_to_bytes, bytes_to_long

# What we know for certain:
# - mind_stone has: 2157869541235478521545895 and secret 83927465839274658392746583
# - Hint says "small exponent" and "repetition"
# - Classic Hastad attack needs e=3 and three (n,c) pairs

# HYPOTHESIS: Maybe the numbers we found ARE enough
# Let me try treating them as the actual RSA values

print("="*70)
print("ATTEMPTING WITH FOUND NUMBERS AS RSA PARAMS")
print("="*70)

# Maybe these are the c values and we need to derive n from file properties?
# Or maybe the challenge is simpler than I thought

# Let's try: what if the secret number IS the plaintext message?
secret = 83927465839274658392746583

# Convert to bytes
msg_bytes = long_to_bytes(secret)
print(f"\nSecret as bytes: {msg_bytes}")
print(f"Secret as hex: {msg_bytes.hex()}")
print(f"Secret as text: {msg_bytes.decode('latin-1', errors='ignore')}")

# Check if it contains flag
if b'Kaal{' in msg_bytes or b'kaal{' in msg_bytes or b'flag' in msg_bytes.lower():
    print(f"\n*** FOUND FLAG: {msg_bytes} ***")

# Try the comment number too
comment = 2157869541235478521545895
comment_bytes = long_to_bytes(comment)
print(f"\nComment as bytes: {comment_bytes}")
print(f"Comment as text: {comment_bytes.decode('latin-1', errors='ignore')}")

# Maybe we need to combine them?
combined = secret + comment
combined_bytes = long_to_bytes(combined)
print(f"\nCombined as text: {combined_bytes.decode('latin-1', errors='ignore')}")

# Or concatenate the byte representations?
concat = msg_bytes + comment_bytes
print(f"\nConcatenated bytes: {concat}")
print(f"Concatenated text: {concat.decode('latin-1', errors='ignore')}")

# Try XOR
xor_val = secret ^ comment
xor_bytes = long_to_bytes(xor_val)
print(f"\nXOR as text: {xor_bytes.decode('latin-1', errors='ignore')}")

# Maybe the secret is base64 encoded?
import base64
try:
    # Try treating the hex as base64
    secret_hex = hex(secret)[2:]
    decoded = base64.b64decode(secret_hex)
    print(f"\nSecret hex as base64: {decoded}")
except:
    pass

# Try treating the bytes as base64
try:
    decoded2 = base64.b64decode(msg_bytes)
    print(f"Secret bytes as base64: {decoded2}")
except:
    pass

# ALTERNATIVE: Maybe I need to look at the actual audio samples
print("\n" + "="*70)
print("EXTRACTING SPECIFIC BYTE RANGES FROM AUDIO")
print("="*70)

# Maybe specific byte offsets contain the RSA params
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone}.wav'
    
    with open(filename, 'rb') as f:
        data = f.read()
        
        # Try specific offsets that might contain hidden data
        # Offset 1000, 2000, 3000, etc.
        for offset in [1000, 2000, 3000, 5000, 10000]:
            chunk = data[offset:offset+50]
            try:
                text = chunk.decode('ascii', errors='ignore')
                if 'Kaal{' in text or 'flag' in text.lower():
                    print(f"\n{stone} at offset {offset}: {text}")
            except:
                pass

# LAST RESORT: Brute force common flag formats
print("\n" + "="*70)
print("TRYING COMMON FLAG PATTERNS")
print("="*70)

# Maybe the numbers encode the flag directly
# Try different encodings of the secret number

# As ASCII codes
secret_str = str(secret)
flag_attempts = []

# Try pairs of digits as ASCII
for i in range(0, len(secret_str)-1, 2):
    pair = secret_str[i:i+2]
    try:
        char = chr(int(pair))
        if char.isprintable():
            flag_attempts.append(char)
    except:
        pass

if flag_attempts:
    potential_flag = ''.join(flag_attempts)
    print(f"Pairs as ASCII: {potential_flag}")
    if 'Kaal' in potential_flag or 'kaal' in potential_flag:
        print(f"*** POTENTIAL FLAG: {potential_flag} ***")

# Try triplets
flag_attempts2 = []
for i in range(0, len(secret_str)-2, 3):
    triplet = secret_str[i:i+3]
    try:
        char = chr(int(triplet))
        if char.isprintable():
            flag_attempts2.append(char)
    except:
        pass

if flag_attempts2:
    potential_flag2 = ''.join(flag_attempts2)
    print(f"Triplets as ASCII: {potential_flag2}")

# Maybe it's ROT13 or Caesar cipher?
import string

def rot13(text):
    result = []
    for char in text:
        if char in string.ascii_lowercase:
            result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
        elif char in string.ascii_uppercase:
            result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
        else:
            result.append(char)
    return ''.join(result)

text_secret = msg_bytes.decode('latin-1', errors='ignore')
print(f"\nROT13 of secret: {rot13(text_secret)}")

# Try all Caesar shifts
for shift in range(1, 26):
    shifted = ''.join(chr((ord(c) - ord('a') + shift) % 26 + ord('a')) if c.islower() 
                      else chr((ord(c) - ord('A') + shift) % 26 + ord('A')) if c.isupper()
                      else c for c in text_secret)
    if 'kaal' in shifted.lower() or 'flag' in shifted.lower():
        print(f"Caesar shift {shift}: {shifted}")

print("\n" + "="*70)
print("If none of these worked, the RSA parameters MUST be on the challenge page")
print("="*70)
