#!/usr/bin/env python3
"""
Ultra-fast solver - try the most likely scenarios first
Maybe the key is shorter or uses specific patterns
"""

from hashlib import md5
import itertools

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

def test_key_simple(key):
    """Test with simplest encryption: CT = (PT XOR MD5(k1)) XOR MD5(k2)"""
    if len(key) < 4:
        return None
    
    k1 = key[:3]
    k2 = key[3:]
    
    md5_k1 = md5(k1).digest()
    md5_k2 = md5(k2).digest()
    
    test_ct = xor_bytes(xor_bytes(known_pt, md5_k1), md5_k2)
    
    if test_ct == known_ct:
        # Decrypt flag
        flag_pt = xor_bytes(xor_bytes(flag_ct, md5_k2), md5_k1)
        return flag_pt
    
    return None

print("=== Ultra-Fast Solver ===\n")

# Strategy 1: Try very short keys (k1=1, k2=1)
print("Strategy 1: Trying k1=1 byte, k2=1 byte...")
for b1 in range(256):
    for b2 in range(256):
        key = bytes([b1, b2, b2, b2])  # Pad to make k1=3, k2=1
        # Actually, let's try k1=1, k2=1 properly
        k1 = bytes([b1])
        k2 = bytes([b2])
        key = k1 + k2
        
        flag = test_key_simple(key)
        if flag:
            print(f"\n*** FOUND! ***")
            print(f"Key: {key.hex()}")
            print(f"Flag: {flag}")
            try:
                print(f"Flag text: {flag.decode('utf-8', errors='ignore')}")
            except:
                pass
            exit(0)

print("Not found with k1=1, k2=1\n")

# Strategy 2: Try k1=1, k2=2
print("Strategy 2: Trying k1=1 byte, k2=2 bytes...")
for b1 in range(256):
    if b1 % 64 == 0:
        print(f"  {b1}/256")
    for b2 in range(256):
        for b3 in range(256):
            key = bytes([b1, b2, b3])
            flag = test_key_simple(key)
            if flag:
                print(f"\n*** FOUND! ***")
                print(f"Key: {key.hex()}")
                print(f"Flag: {flag}")
                try:
                    print(f"Flag text: {flag.decode('utf-8', errors='ignore')}")
                except:
                    pass
                exit(0)

print("Not found with k1=1, k2=2\n")

# Strategy 3: Try k1=1, k2=3
print("Strategy 3: Trying k1=1 byte, k2=3 bytes...")
for b1 in range(256):
    if b1 % 32 == 0:
        print(f"  {b1}/256")
    for b2 in range(256):
        for b3 in range(256):
            for b4 in range(256):
                key = bytes([b1, b2, b3, b4])
                flag = test_key_simple(key)
                if flag:
                    print(f"\n*** FOUND! ***")
                    print(f"Key: {key.hex()}")
                    print(f"Flag: {flag}")
                    try:
                        print(f"Flag text: {flag.decode('utf-8', errors='ignore')}")
                    except:
                        pass
                    exit(0)

print("Not found with k1=1, k2=3\n")

# Strategy 4: Maybe k1 is NOT 3 bytes? Try k1=4, k2=2
print("Strategy 4: Trying k1=4 bytes, k2=2 bytes (limited search)...")
# This is too large, try just first 1M
for i in range(1000000):
    if i % 100000 == 0:
        print(f"  {i}/1000000")
    
    # k1 = 4 bytes
    k1 = bytes([
        i & 0xFF,
        (i >> 8) & 0xFF,
        (i >> 16) & 0xFF,
        (i >> 24) & 0xFF
    ])
    
    # k2 = 2 bytes (try a few)
    for b1 in range(min(256, 10)):
        for b2 in range(min(256, 10)):
            k2 = bytes([b1, b2])
            key = k1 + k2
            
            flag = test_key_simple(key)
            if flag:
                print(f"\n*** FOUND! ***")
                print(f"Key: {key.hex()}")
                print(f"Flag: {flag}")
                try:
                    print(f"Flag text: {flag.decode('utf-8', errors='ignore')}")
                except:
                    pass
                exit(0)

print("\nNo quick solution found.")
print("The key space is likely larger. Consider:")
print("1. Running the continuous_solver.py for several hours")
print("2. Using distributed computing")
print("3. Looking for additional hints in the challenge materials")
