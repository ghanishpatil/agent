#!/usr/bin/env python3
"""
Reverse engineer the flag decoding
Based on the encoded string and the pattern, try common algorithms
"""
import base64
import string

encoded = "AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc"

print("="*60)
print("REVERSE ENGINEERING FLAG DECODE")
print("="*60)

# The functions are named a1, a2, a3, a4, d1, d2
# This suggests: a = add/encode, d = decode
# Likely a custom base64 or substitution cipher

# Try custom base64 alphabets
print("\n[1] Trying custom base64 alphabets:")

# Standard base64 alphabet
std_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

# Common variations
alphabets = [
    std_alphabet,
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_",  # URL-safe
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/",  # Digits first
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/",  # Lowercase first
]

for i, alphabet in enumerate(alphabets):
    try:
        # Create translation table
        trans = str.maketrans(alphabet, std_alphabet)
        normalized = encoded.translate(trans)
        
        # Try to decode
        for padding in ['', '=', '==', '===']:
            try:
                decoded = base64.b64decode(normalized + padding)
                decoded_str = decoded.decode('utf-8', errors='ignore')
                if decoded_str and all(c in string.printable for c in decoded_str):
                    print(f"    Alphabet {i}, padding '{padding}': {decoded_str}")
                    if 'Kaal' in decoded_str or len(decoded_str) > 10:
                        print(f"        *** POTENTIAL: {decoded_str} ***")
            except:
                pass
    except:
        pass

# Try simple substitution based on the pattern
print("\n[2] Analyzing character frequency:")
char_freq = {}
for c in encoded:
    char_freq[c] = char_freq.get(c, 0) + 1

print(f"    Character frequency: {char_freq}")

# Try reversing the string
print("\n[3] Reversed string:")
reversed_str = encoded[::-1]
print(f"    {reversed_str}")

# Try base64 decode of reversed
for padding in ['', '=', '==']:
    try:
        decoded = base64.b64decode(reversed_str + padding)
        decoded_str = decoded.decode('utf-8', errors='ignore')
        if decoded_str:
            print(f"        With padding '{padding}': {decoded_str}")
    except:
        pass

# Try interpreting as hex pairs
print("\n[4] Trying as hex-encoded:")
try:
    # Take pairs of characters as hex
    hex_str = ''
    for i in range(0, len(encoded), 2):
        if i+1 < len(encoded):
            hex_str += encoded[i:i+2]
    
    decoded = bytes.fromhex(hex_str)
    print(f"    Decoded: {decoded}")
except Exception as e:
    print(f"    Error: {e}")

# The string might be a key to XOR with something else
print("\n[5] Trying XOR with common patterns:")
# XOR with "Kaal{" to see if we can find a pattern
kaal = b'Kaal{'
for i in range(min(len(encoded), len(kaal))):
    xor_val = ord(encoded[i]) ^ kaal[i]
    print(f"    encoded[{i}] ('{encoded[i]}') XOR kaal[{i}] ('{chr(kaal[i])}') = 0x{xor_val:02x}")

print("\n" + "="*60)
