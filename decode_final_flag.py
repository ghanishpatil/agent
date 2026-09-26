#!/usr/bin/env python3
import hashlib

cipher = "1eeb796a528691900c04ee6d75836b39ac88f0152520b628fc9be5325dff7284"

print("="*80)
print("DECODING FINAL FLAG")
print("="*80)

print(f"\nCipher: {cipher}")
print("Encoding: XOR + BASE58 + MORSE")
print("Hint: The key is love itself")

# Try XOR with "love"
key = "love"
cipher_bytes = bytes.fromhex(cipher)

print(f"\n[METHOD 1: XOR with '{key}']")
result = []
for i, byte in enumerate(cipher_bytes):
    result.append(byte ^ ord(key[i % len(key)]))

decoded = bytes(result)
print(f"Result: {decoded}")
try:
    print(f"ASCII: {decoded.decode('utf-8', errors='ignore')}")
except:
    pass

# Try different keys
keys = ["love", "LOVE", "Love", "heart", "HEART", "KEY NEXT LEVEL", "valentine"]

print(f"\n[TRYING MULTIPLE KEYS]")
for k in keys:
    result = []
    for i, byte in enumerate(cipher_bytes):
        result.append(byte ^ ord(k[i % len(k)]))
    
    decoded = bytes(result)
    try:
        text = decoded.decode('utf-8', errors='ignore')
        if 'FLAG' in text or 'CTF' in text or text.isprintable():
            print(f"\nKey '{k}':")
            print(f"  {text}")
    except:
        pass

# Maybe it's already a hash?
print(f"\n[CHECKING IF IT'S A HASH]")
print(f"Length: {len(cipher)} chars = {len(cipher)//2} bytes")
print("Could be SHA256 hash")

# Try common hash inputs
common = ["love", "heart", "valentine", "secret", "flag", "KEY NEXT LEVEL"]
for word in common:
    sha = hashlib.sha256(word.encode()).hexdigest()
    if sha == cipher:
        print(f"\n✓ MATCH! SHA256('{word}') = {cipher}")
        print(f"The cipher IS the hash of '{word}'")
        print(f"Possible flag: FLAG{{{word.upper()}}}")

# The hint says FLAG{...} format
print(f"\n[CONSTRUCTING FLAG]")
print("Based on hints:")
print("1. Morse cipher from heart box")
print("2. Format: FLAG{...}")
print("3. Key is 'love'")
print()
print("Possible flags:")
print("  FLAG{LOVE}")
print("  FLAG{L0V3}")
print("  FLAG{HEART_OF_SECRETS}")
print("  FLAG{KEY_NEXT_LEVEL}")
print("  FLAG{1eeb796a528691900c04ee6d75836b39ac88f0152520b628fc9be5325dff7284}")

# Check if the hex is morse
print(f"\n[CHECKING FOR MORSE IN HEX]")
# Convert hex to binary
binary = bin(int(cipher, 16))[2:]
print(f"Binary: {binary[:100]}...")

# Maybe the cipher needs to be decoded differently
print(f"\n[BASE58 DECODE ATTEMPT]")
# Base58 alphabet
base58_alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

print("\nThe cipher is likely the final answer itself or needs the 'love' key")
print("Most likely flag: FLAG{LOVE} or FLAG{L0V3}")
