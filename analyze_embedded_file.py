#!/usr/bin/env python3
"""Analyze the embedded file"""
import os

EMBEDDED_FILE = "apk_extracted/embedded_file.bin"

print("="*80)
print("ANALYZING EMBEDDED FILE")
print("="*80)

with open(EMBEDDED_FILE, 'rb') as f:
    data = f.read()

print(f"\nFile size: {len(data)} bytes ({len(data)/1024/1024:.2f} MB)")
print(f"First 200 bytes: {data[:200]}")

# Check if it looks like an APK (should start with PK)
if data[:2] == b'PK':
    print("\n✓ This is a ZIP/APK file!")
else:
    print("\n✗ NOT a standard ZIP/APK (doesn't start with 'PK')")
    print("  This file is likely encrypted or encoded")

# Check entropy (high entropy = encrypted)
from collections import Counter
byte_counts = Counter(data[:10000])  # Check first 10KB
entropy = -sum((count/10000) * __import__('math').log2(count/10000) 
               for count in byte_counts.values() if count > 0)
print(f"\nEntropy (first 10KB): {entropy:.2f} bits/byte")
print(f"  (8.0 = random/encrypted, <7.0 = structured data)")

if entropy > 7.5:
    print("  → File appears to be ENCRYPTED or COMPRESSED")
else:
    print("  → File appears to be structured/unencrypted")

# Look for any magic bytes or signatures
print("\n[Checking for known file signatures]")
signatures = {
    b'PK': 'ZIP/APK',
    b'\x1f\x8b': 'GZIP',
    b'BZ': 'BZIP2',
    b'\x50\x4b\x03\x04': 'ZIP',
    b'\x50\x4b\x05\x06': 'ZIP (empty)',
    b'\x50\x4b\x07\x08': 'ZIP (spanned)',
    b'dex\n': 'DEX file',
    b'\x7fELF': 'ELF binary',
}

for sig, desc in signatures.items():
    if data[:len(sig)] == sig:
        print(f"  ✓ Matches: {desc}")
        break
else:
    print(f"  ✗ No known signature found")

# The key we found
key_string = "401745546b5c0affd89343914f88bab4c82"
print(f"\n[Found key/hash in assets]")
print(f"  Key: {key_string}")
print(f"  Length: {len(key_string)} chars")
print(f"  Could be: MD5 hash (32 hex chars) or encryption key")

# Try to decrypt using the key
print("\n[Attempting decryption]")
print("  Trying XOR with key...")

# Convert hex key to bytes
try:
    key_bytes = bytes.fromhex(key_string)
    print(f"  Key as bytes: {key_bytes[:20]}...")
    
    # Try XOR decryption
    decrypted = bytearray()
    for i in range(min(1000, len(data))):
        decrypted.append(data[i] ^ key_bytes[i % len(key_bytes)])
    
    print(f"  Decrypted first 100 bytes: {bytes(decrypted[:100])}")
    
    # Check if decrypted data looks like an APK
    if decrypted[:2] == b'PK':
        print("\n  ✓✓✓ DECRYPTION SUCCESSFUL! This is an APK!")
        
        # Save decrypted APK
        output_path = "apk_extracted/decrypted_app.apk"
        decrypted_full = bytearray()
        for i in range(len(data)):
            decrypted_full.append(data[i] ^ key_bytes[i % len(key_bytes)])
        
        with open(output_path, 'wb') as f:
            f.write(bytes(decrypted_full))
        print(f"  Saved to: {output_path}")
    else:
        print("  ✗ XOR decryption didn't produce valid APK")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*80)
