#!/usr/bin/env python3
"""
Analyze the crypto structure to find patterns or shortcuts
"""

from hashlib import md5

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

print("=== Analyzing Crypto Challenge ===\n")

# Check if there's a simple XOR relationship
xor_result = bytes([a ^ b for a, b in zip(known_pt, known_ct)])
print(f"PT XOR CT: {xor_result.hex()}")
print(f"PT XOR CT (bytes): {xor_result}")
print()

# Check if the XOR result looks like an MD5 hash (16 bytes)
print(f"Length of PT: {len(known_pt)}")
print(f"Length of CT: {len(known_ct)}")
print(f"Length of XOR: {len(xor_result)}")
print()

# Maybe the key is hidden in the plaintext or ciphertext?
print("Looking for patterns...")
print(f"PT as ASCII (ignore errors): {known_pt.decode('latin-1')}")
print(f"CT as ASCII (ignore errors): {known_ct.decode('latin-1')}")
print()

# What if ROUNDS=0 and it's just double XOR?
# CT = (PT XOR MD5(k1)) XOR MD5(k2)
# Then: PT XOR CT = MD5(k1) XOR MD5(k2)

print("If it's double XOR with MD5 hashes:")
print("PT XOR CT = MD5(k1) XOR MD5(k2)")
print()

# Let's try common keys
common_keys = [
    b"key",
    b"password",
    b"secret",
    b"flag",
    b"test",
    b"admin",
    b"root",
    b"kaal",
    b"Kaal",
    b"KAAL",
]

print("Trying common key patterns...")
for base_key in common_keys:
    # Try different lengths
    for k1_len in [3]:
        for k2_len in [3, 4, 5, 8, 13]:
            k1 = base_key[:k1_len].ljust(k1_len, b'\x00')
            k2 = base_key[k1_len:k1_len+k2_len].ljust(k2_len, b'\x00')
            
            # Test if MD5(k1) XOR MD5(k2) = PT XOR CT
            md5_k1 = md5(k1).digest()
            md5_k2 = md5(k2).digest()
            xor_keys = bytes([a ^ b for a, b in zip(md5_k1, md5_k2)])
            
            if xor_keys == xor_result:
                print(f"\n*** POTENTIAL MATCH! ***")
                print(f"Base key: {base_key}")
                print(f"k1: {k1.hex()} = {k1}")
                print(f"k2: {k2.hex()} = {k2}")
                print(f"Full key: {(k1+k2).hex()}")
                
                # Decrypt flag
                flag_xor = bytes([a ^ b for a, b in zip(md5_k1, md5_k2)])
                flag_pt = bytes([a ^ b for a, b in zip(flag_ct, flag_xor)])
                
                print(f"\nFlag (hex): {flag_pt.hex()}")
                print(f"Flag (bytes): {flag_pt}")
                try:
                    flag_text = flag_pt.decode('utf-8', errors='ignore')
                    print(f"Flag (text): {flag_text}")
                except:
                    pass

print("\n" + "="*50)
print("Alternative approach: What if we can derive the key from the known pair?")
print("="*50)

# If the encryption is weak, maybe we can extract the key directly
# Let's see if there's a relationship

# Try to see if the key might be embedded in the plaintext or ciphertext
for i in range(len(known_pt) - 5):
    potential_key = known_pt[i:i+6]
    print(f"Potential key from PT[{i}:{i+6}]: {potential_key.hex()}")

print()

for i in range(len(known_ct) - 5):
    potential_key = known_ct[i:i+6]
    print(f"Potential key from CT[{i}:{i+6}]: {potential_key.hex()}")
