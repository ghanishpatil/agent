#!/usr/bin/env python3
"""
Final attempt - look for RSA params in standard CTF formats
"""

import re

# Check if there's a README or params file we missed
import os
files = os.listdir('stones_extracted')
print("Files in stones_extracted:")
for f in files:
    print(f"  {f}")

# Look for any .txt files in current directory that might have params
all_files = [f for f in os.listdir('.') if f.endswith('.txt') or f.endswith('.md')]
print("\nText files in current directory:")
for f in all_files[:20]:
    print(f"  {f}")

# Maybe the challenge description itself has the params
# Let me create a solver that works with typical CTF Hastad examples

print("\n" + "="*70)
print("CHECKING IF PARAMS ARE IN CHALLENGE DESCRIPTION")
print("="*70)

# The user said the challenge is from a CTF platform
# Typically, the RSA parameters would be:
# 1. In the challenge description
# 2. In a separate file
# 3. Embedded in the audio files in a specific way

# Let me try one more thing - check if the filenames or metadata encode something
print("\nFilename analysis:")
print("soul_stone_1st - 1st suggests first encryption")
print("time_stone_2nd - 2nd suggests second encryption")
print("mind_stone_3rd - 3rd suggests third encryption")

# The secret we found: 83927465839274658392746583
# This is 26 digits, which is too small for RSA
# But maybe it's hex?

secret_dec = 83927465839274658392746583
secret_hex = hex(secret_dec)
print(f"\nSecret number: {secret_dec}")
print(f"As hex: {secret_hex}")
print(f"Bit length: {secret_dec.bit_length()}")

# Try to decode as bytes
from Crypto.Util.number import long_to_bytes
try:
    msg = long_to_bytes(secret_dec)
    print(f"As bytes: {msg}")
    print(f"As text: {msg.decode('utf-8', errors='ignore')}")
    
    if b'Kaal{' in msg or b'kaal{' in msg or b'flag' in msg.lower():
        print(f"\n*** POTENTIAL FLAG: {msg} ***")
except Exception as e:
    print(f"Error: {e}")

# Also try the comment number
comment_num = 2157869541235478521545895
try:
    msg2 = long_to_bytes(comment_num)
    print(f"\nComment as bytes: {msg2}")
    print(f"Comment as text: {msg2.decode('utf-8', errors='ignore')}")
except:
    pass

# Maybe we need to XOR them or combine them somehow?
print("\n" + "="*70)
print("TRYING COMBINATIONS")
print("="*70)

# XOR the two numbers
xor_result = secret_dec ^ comment_num
print(f"XOR result: {xor_result}")
try:
    msg3 = long_to_bytes(xor_result)
    print(f"XOR as text: {msg3.decode('utf-8', errors='ignore')}")
except:
    pass

# Maybe multiply?
mult_result = secret_dec * comment_num
print(f"\nProduct bit length: {mult_result.bit_length()}")

# Or maybe the secret IS the plaintext message and we need to verify?
print("\n" + "="*70)
print("HYPOTHESIS: Secret number IS the decrypted message")
print("="*70)
print(f"If M = {secret_dec}")
print(f"Then M^3 = {secret_dec ** 3}")
print("This should equal the ciphertext when reduced mod n")
