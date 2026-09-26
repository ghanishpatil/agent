#!/usr/bin/env python3
"""
Smart solver - maybe the missing parameters have specific values we can deduce
"""

from hashlib import md5

BLOCK_SIZE = 16

def xor(a, b):
    return bytes([x^y for x, y in zip(a, b)])

# Load known pair
known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

print("Analyzing the structure...")
print(f"Known PT: {known_pt.hex()}")
print(f"Known CT: {known_ct.hex()}")
print(f"Flag CT:  {flag_ct.hex()}")
print()

# Key insight: If ROUNDS=0, then fun() just returns the input unchanged
# Let's test if ROUNDS might be 0 or very small

def fun_rounds_0(key, pt):
    """If ROUNDS=0, fun just returns pt"""
    return pt

def encrypt_rounds_0(key, pt):
    k1 = key[:3]
    k2 = key[3:]
    return fun_rounds_0(k2, fun_rounds_0(k1, pt))

# Test ROUNDS=0
if encrypt_rounds_0(b"test", known_pt) == known_pt:
    print("ROUNDS=0 would mean CT=PT, but that's not the case")
print()

# Maybe the parameters are such that we can work backwards
# Let's try to see if there's a pattern

# Another approach: What if SBOX and PERM are identity, and ROUNDS=1?
# Then: fun(key, pt) = PERM(SBOX(pt XOR md5(key)))
# With identity: fun(key, pt) = pt XOR md5(key)

def fun_simple(key, pt):
    """Simplified fun with identity SBOX and PERM, ROUNDS=1"""
    key_hash = md5(key).digest()
    return xor(pt, key_hash)

def encrypt_simple(key, pt):
    k1 = key[:3]
    k2 = key[3:]
    intermediate = fun_simple(k1, pt)
    return fun_simple(k2, intermediate)

def decrypt_simple(key, ct):
    k1 = key[:3]
    k2 = key[3:]
    intermediate = fun_simple(k2, ct)  # XOR is its own inverse
    return fun_simple(k1, intermediate)

print("Testing simplified version (identity SBOX/PERM, ROUNDS=1)...")
print("This means: CT = (PT XOR MD5(k1)) XOR MD5(k2)")
print()

# With this simplification, we can use meet-in-the-middle more efficiently
# Build table of PT XOR MD5(k1) for all 3-byte k1
print("Building forward table for 3-byte k1 values...")

forward_table = {}
for b1 in range(256):
    if b1 % 32 == 0:
        print(f"  Progress: {b1}/256")
    for b2 in range(256):
        for b3 in range(256):
            k1 = bytes([b1, b2, b3])
            intermediate = fun_simple(k1, known_pt)
            forward_table[intermediate] = k1

print(f"Built table with {len(forward_table)} entries")
print()

# Now try different k2 lengths
print("Searching for matching k2...")

for k2_len in [3, 4, 5, 8, 13]:
    print(f"\nTrying k2 length: {k2_len}")
    
    if k2_len <= 4:
        # Brute force
        from itertools import product
        count = 0
        for k2_bytes in product(range(256), repeat=k2_len):
            k2 = bytes(k2_bytes)
            # What we need: intermediate = CT XOR MD5(k2)
            intermediate = fun_simple(k2, known_ct)
            
            if intermediate in forward_table:
                k1 = forward_table[intermediate]
                key = k1 + k2
                
                # Verify
                test_ct = encrypt_simple(key, known_pt)
                if test_ct == known_ct:
                    print(f"\n*** FOUND KEY! ***")
                    print(f"k1: {k1.hex()} = {k1}")
                    print(f"k2: {k2.hex()} = {k2}")
                    print(f"Full key: {key.hex()} = {key}")
                    
                    # Decrypt flag
                    flag_pt = decrypt_simple(key, flag_ct)
                    print(f"\nFlag (hex): {flag_pt.hex()}")
                    print(f"Flag (bytes): {flag_pt}")
                    
                    try:
                        flag_text = flag_pt.decode('utf-8', errors='ignore')
                        print(f"Flag (text): {flag_text}")
                    except:
                        pass
                    
                    # Check if it starts with "Kaal" (the flag format)
                    if flag_pt.startswith(b'Kaal'):
                        print("\n✓ Flag format matches! (starts with 'Kaal')")
                    
                    exit(0)
            
            count += 1
            if count % 1000000 == 0:
                print(f"  Checked {count} k2 values...")

print("\nNo solution found.")
