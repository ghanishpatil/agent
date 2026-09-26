#!/usr/bin/env python3
"""
Rethink the problem - maybe the missing values can be deduced from context
or there's a specific weakness we should exploit
"""

from hashlib import md5

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

print("=== Rethinking the Challenge ===\n")

# What if the key is actually in the plaintext or ciphertext?
# Or what if there's a standard key being used?

# Let's try keys that might be related to "Kaal" (the flag format)
test_keys = [
    b"Kaal",
    b"kaal",
    b"KAAL",
    b"Kaalchakra",
    b"kaalchakra",
    b"KAALCHAKRA",
    b"flag",
    b"FLAG",
    b"key",
    b"KEY",
    b"secret",
    b"SECRET",
    b"password",
    b"PASSWORD",
    b"crypto",
    b"CRYPTO",
    b"cipher",
    b"CIPHER",
]

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

def test_key(key):
    """Test if a key works with simple double-XOR"""
    if len(key) < 4:
        return False
    
    k1 = key[:3]
    k2 = key[3:]
    
    md5_k1 = md5(k1).digest()
    md5_k2 = md5(k2).digest()
    
    # Encrypt: CT = (PT XOR MD5(k1)) XOR MD5(k2)
    test_ct = xor_bytes(xor_bytes(known_pt, md5_k1), md5_k2)
    
    if test_ct == known_ct:
        print(f"\n*** KEY FOUND! ***")
        print(f"Key: {key}")
        print(f"Key (hex): {key.hex()}")
        print(f"k1: {k1.hex()}")
        print(f"k2: {k2.hex()}")
        
        # Decrypt flag
        flag_pt = xor_bytes(xor_bytes(flag_ct, md5_k2), md5_k1)
        print(f"\nFlag (hex): {flag_pt.hex()}")
        print(f"Flag (bytes): {flag_pt}")
        
        try:
            flag_text = flag_pt.decode('utf-8', errors='ignore')
            print(f"Flag (text): {flag_text}")
        except:
            pass
        
        return True
    
    return False

print("Testing common keys...")
for base_key in test_keys:
    # Try the key as-is
    if test_key(base_key):
        exit(0)
    
    # Try with padding
    for length in [6, 8, 16, 32]:
        padded = base_key.ljust(length, b'\x00')
        if test_key(padded):
            exit(0)
        
        padded = base_key.ljust(length, b' ')
        if test_key(padded):
            exit(0)

print("\nCommon keys didn't work.")
print("\nLet's think about the structure differently...")
print()

# What if ROUNDS, SBOX, PERM being None means they're not used at all?
# Maybe the encryption is even simpler?

print("Testing if encryption is just: CT = PT XOR MD5(key)")
for base_key in test_keys:
    for length in [3, 4, 5, 6, 8, 16]:
        key = base_key.ljust(length, b'\x00')[:length]
        
        md5_key = md5(key).digest()
        test_ct = xor_bytes(known_pt, md5_key)
        
        if test_ct == known_ct:
            print(f"\n*** SIMPLE KEY FOUND! ***")
            print(f"Key: {key}")
            print(f"Key (hex): {key.hex()}")
            
            # Decrypt flag
            flag_pt = xor_bytes(flag_ct, md5_key)
            print(f"\nFlag: {flag_pt}")
            try:
                print(f"Flag text: {flag_pt.decode('utf-8', errors='ignore')}")
            except:
                pass
            
            exit(0)

print("\nSimple XOR didn't work either.")
print()

# Maybe we need to look at the actual values more carefully
print("Analyzing the hex values...")
print(f"PT: {known_pt.hex()}")
print(f"CT: {known_ct.hex()}")
print(f"XOR: {xor_bytes(known_pt, known_ct).hex()}")
print()

# Check if XOR result is a valid MD5 hash of something simple
xor_result = xor_bytes(known_pt, known_ct)
print("Checking if PT XOR CT is MD5 of common strings...")

for test_str in [b"", b"0", b"1", b"key", b"flag", b"test", b"password"]:
    if md5(test_str).digest() == xor_result:
        print(f"\n*** PT XOR CT = MD5('{test_str.decode()}') ***")
        print("This means the encryption might be: CT = PT XOR MD5(key)")
        print(f"And the key is: {test_str}")
        
        # Decrypt flag
        flag_pt = xor_bytes(flag_ct, xor_result)
        print(f"\nFlag: {flag_pt}")
        try:
            print(f"Flag text: {flag_pt.decode('utf-8', errors='ignore')}")
        except:
            pass
        
        exit(0)

print("\nNo simple pattern found. The key space might be larger than expected.")
print("Consider:")
print("1. k1 might be 3 bytes, k2 might be 4+ bytes")
print("2. SBOX and PERM might not be identity")
print("3. ROUNDS might be > 1")
print("\nA full brute force would require significant compute time.")
