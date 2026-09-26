#!/usr/bin/env python3
"""
Extract the actual decode logic by analyzing the binary more carefully
The functions d1 and d2 are the decode functions
"""

# Read binary
with open('game/game.exe', 'rb') as f:
    data = f.read()

print("="*60)
print("EXTRACTING DECODE LOGIC")
print("="*60)

# Find where the encoded string is used
encoded_str = b'AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc'
encoded_pos = data.find(encoded_str)

print(f"\nEncoded string at: 0x{encoded_pos:x}")

# Look for references to this address in the code
# In x86-64, this would be LEA instructions or direct references

# Let's look at what's immediately after the encoded string
after_encoded = data[encoded_pos + len(encoded_str):encoded_pos + len(encoded_str) + 100]
print(f"\nData after encoded string:")
print(f"  Hex: {after_encoded[:50].hex()}")
print(f"  ASCII: {after_encoded[:50].decode('ascii', errors='ignore')}")

# Look for "Kaal{" and "}" to see how the flag is constructed
kaal_pos = data.find(b'Kaal{')
print(f"\n'Kaal{{' at: 0x{kaal_pos:x}")

brace_pos = data.find(b'}', kaal_pos)
print(f"'}}' at: 0x{brace_pos:x}")

# Distance between them
distance = brace_pos - kaal_pos
print(f"Distance: {distance} bytes")

# If distance is small (like 6), the flag content is inserted between them
# Let's see what's between Kaal{ and }
between = data[kaal_pos:brace_pos+1]
print(f"Between Kaal{{ and }}: {between}")

# The flag is likely: Kaal{ + decoded_string + }
# Let's try to find the decode algorithm by looking at common patterns

# Base64 uses a lookup table
# Let's search for base64-like lookup tables in the binary
print("\n[Searching for base64 alphabet]:")
std_b64 = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
if std_b64 in data:
    pos = data.find(std_b64)
    print(f"  Standard base64 alphabet at: 0x{pos:x}")

# Look for custom alphabets
custom_alphabets = [
    b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
]

for alphabet in custom_alphabets:
    if alphabet in data:
        pos = data.find(alphabet)
        print(f"  Custom alphabet at: 0x{pos:x}: {alphabet[:20]}...")

# Let's try a different approach - maybe the string is already the flag
# and just needs to be formatted correctly

print("\n[Final decode attempts]:")

# The encoded string might be base64 with URL-safe alphabet
import base64

encoded = "AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc"

# Try treating underscores and other chars specially
# URL-safe base64 uses - and _ instead of + and /
url_safe_encoded = encoded.replace('_', '/')

for padding in ['', '=', '==']:
    try:
        decoded = base64.b64decode(url_safe_encoded + padding)
        decoded_str = decoded.decode('utf-8', errors='ignore')
        if decoded_str:
            print(f"  URL-safe decode (padding '{padding}'): {decoded_str}")
            print(f"    Kaal{{{decoded_str}}}")
    except:
        pass

# Maybe it's a simple XOR with a repeating key
print("\n[XOR with repeating keys]:")
keys = [b'game', b'flag', b'kaal', b'ctf', b'key', b'decode']

for key in keys:
    decoded = ''
    for i, c in enumerate(encoded):
        decoded += chr(ord(c) ^ key[i % len(key)])
    
    # Check if printable
    if all(32 <= ord(c) < 127 for c in decoded):
        print(f"  Key '{key.decode()}': {decoded}")
        print(f"    Kaal{{{decoded}}}")

print("\n" + "="*60)
