#!/usr/bin/env python3
"""Decrypt the embedded APK using the key"""

ENCRYPTED_FILE = "apk_extracted/embedded_1.bin"
KEY_STRING = "401745546b5c0affd89343914f88bab4c82"

print("="*80)
print("DECRYPTING EMBEDDED APK")
print("="*80)

# Read encrypted data
with open(ENCRYPTED_FILE, 'rb') as f:
    encrypted = f.read()

print(f"\nEncrypted file size: {len(encrypted)} bytes")
print(f"Key: {KEY_STRING}")
print(f"Key length: {len(KEY_STRING)} chars")

# The key might be hex, but it's 35 chars (odd number)
# Let's try different approaches

# Approach 1: Use key as-is (ASCII bytes)
print("\n[Approach 1: Using key as ASCII bytes]")
key_bytes = KEY_STRING.encode('ascii')
print(f"Key as bytes: {key_bytes}")

decrypted = bytearray()
for i in range(len(encrypted)):
    decrypted.append(encrypted[i] ^ key_bytes[i % len(key_bytes)])

print(f"First 100 decrypted bytes: {bytes(decrypted[:100])}")

if decrypted[:2] == b'PK':
    print("✓✓✓ SUCCESS! Decrypted data is a ZIP/APK!")
    output_path = "apk_extracted/decrypted_app.apk"
    with open(output_path, 'wb') as f:
        f.write(bytes(decrypted))
    print(f"Saved to: {output_path}")
else:
    print("✗ Not a valid ZIP/APK")

# Approach 2: Try first 32 chars as hex
print("\n[Approach 2: Using first 32 chars as hex]")
try:
    key_hex = bytes.fromhex(KEY_STRING[:32])
    print(f"Key as hex bytes: {key_hex}")
    
    decrypted2 = bytearray()
    for i in range(len(encrypted)):
        decrypted2.append(encrypted[i] ^ key_hex[i % len(key_hex)])
    
    print(f"First 100 decrypted bytes: {bytes(decrypted2[:100])}")
    
    if decrypted2[:2] == b'PK':
        print("✓✓✓ SUCCESS! Decrypted data is a ZIP/APK!")
        output_path = "apk_extracted/decrypted_app_hex.apk"
        with open(output_path, 'wb') as f:
            f.write(bytes(decrypted2))
        print(f"Saved to: {output_path}")
    else:
        print("✗ Not a valid ZIP/APK")
except Exception as e:
    print(f"Error: {e}")

# Approach 3: Maybe it's not XOR, try other methods
print("\n[Approach 3: Checking if it's just compressed]")
import gzip
import zlib

# Try gzip
try:
    decompressed = gzip.decompress(encrypted)
    print(f"✓ GZIP decompression successful!")
    if decompressed[:2] == b'PK':
        print("✓✓✓ Decompressed data is a ZIP/APK!")
        with open("apk_extracted/decompressed_app.apk", 'wb') as f:
            f.write(decompressed)
except:
    print("✗ Not GZIP compressed")

# Try zlib
try:
    decompressed = zlib.decompress(encrypted)
    print(f"✓ ZLIB decompression successful!")
    if decompressed[:2] == b'PK':
        print("✓✓✓ Decompressed data is a ZIP/APK!")
        with open("apk_extracted/decompressed_app_zlib.apk", 'wb') as f:
            f.write(decompressed)
except:
    print("✗ Not ZLIB compressed")

print("\n" + "="*80)
