#!/usr/bin/env python3
"""Try to decode the password from the hex"""

hex_string = "9fa1a79fa4a3a8a4a2a0a4a79fa1a8a4a8a0a2a6a2a1a2a8a3a7a8a2a5a09f9fa2a4a1a3a2a0a4a89fa1a3a8a4a4a49fa8a8"

print("="*80)
print("DECODING PASSWORD")
print("="*80)

print(f"\nHex string: {hex_string}")
print(f"Length: {len(hex_string)} chars ({len(hex_string)//2} bytes)")

# Convert to bytes
data = bytes.fromhex(hex_string)
print(f"\nAs bytes: {data}")

# Try different decodings
print("\n[Trying different decodings]")

# ASCII
try:
    print(f"ASCII: {data.decode('ascii')}")
except:
    print("ASCII: Failed")

# UTF-8
try:
    print(f"UTF-8: {data.decode('utf-8')}")
except:
    print("UTF-8: Failed")

# Latin-1
try:
    decoded = data.decode('latin-1')
    print(f"Latin-1: {decoded}")
    print(f"Repr: {repr(decoded)}")
except:
    print("Latin-1: Failed")

# Maybe it's base64 encoded?
import base64
try:
    decoded = base64.b64decode(data)
    print(f"Base64: {decoded}")
except:
    print("Base64: Failed")

# Maybe the bytes represent something else
# Let's try XOR with common values
print("\n[Trying XOR transformations]")
for xor_val in [0x80, 0xff, 0xaa, 0x55]:
    result = bytes([b ^ xor_val for b in data])
    try:
        decoded = result.decode('ascii', errors='ignore')
        if decoded.isprintable() and len(decoded) > 5:
            print(f"XOR with 0x{xor_val:02x}: {decoded}")
    except:
        pass

# Maybe subtract 0x80 or 0x9f (offset)
print("\n[Trying offset transformations]")
for offset in [0x80, 0x9f, 0xa0]:
    result = bytes([(b - offset) & 0xff for b in data])
    try:
        decoded = result.decode('ascii', errors='ignore')
        if decoded.isprintable() and len(decoded) > 5:
            print(f"Subtract 0x{offset:02x}: {decoded}")
    except:
        pass

# The key itself might be the password
print("\n[Checking the key]")
key = "401745546b5c0affd89343914f88bab4c82"
print(f"Key: {key}")
print(f"First 10 chars: {key[:10]}")
print(f"Last 10 chars: {key[-10:]}")

# Maybe decode parts of the key as hex
try:
    key_decoded = bytes.fromhex(key[:32])  # First 32 chars (16 bytes)
    print(f"Key (first 32 chars) as bytes: {key_decoded}")
    print(f"As ASCII: {key_decoded.decode('ascii', errors='ignore')}")
except:
    pass

print("\n" + "="*80)
print("\nTRY THESE PASSWORDS:")
print("1. 401745546b5c0affd89343914f88bab4c82 (the full key)")
print("2. 40174554 (first 8 chars)")
print("3. raj045735 (author)")
print("="*80)
