#!/usr/bin/env python3
"""
Optimized MITM attack - use multiprocessing and focus on likely key spaces
"""

from hashlib import md5
from multiprocessing import Pool, Manager
import itertools

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

# The target: PT XOR CT = MD5(k1) XOR MD5(k2)
target_xor = bytes([a ^ b for a, b in zip(known_pt, known_ct)])

print(f"Target XOR: {target_xor.hex()}")
print()

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

# Build forward table more efficiently - only store hash of intermediate
print("Building forward table for k1 (3 bytes)...")
forward_table = {}

for b1 in range(256):
    if b1 % 64 == 0:
        print(f"  {b1}/256")
    for b2 in range(256):
        for b3 in range(256):
            k1 = bytes([b1, b2, b3])
            md5_k1 = md5(k1).digest()
            intermediate = xor_bytes(known_pt, md5_k1)
            forward_table[intermediate] = k1

print(f"Forward table built: {len(forward_table)} entries\n")

# Now search for k2
def check_k2_range(start, end, k2_len):
    """Check a range of k2 values"""
    results = []
    for i in range(start, end):
        # Convert i to bytes
        k2_bytes = []
        temp = i
        for _ in range(k2_len):
            k2_bytes.append(temp % 256)
            temp //= 256
        k2 = bytes(k2_bytes)
        
        md5_k2 = md5(k2).digest()
        intermediate = xor_bytes(known_ct, md5_k2)
        
        if intermediate in forward_table:
            k1 = forward_table[intermediate]
            results.append((k1, k2))
    
    return results

# Try k2 length = 3 first (most feasible)
k2_len = 3
total_k2 = 256 ** k2_len
print(f"Searching k2 space (length={k2_len}, total={total_k2})...")

# Check in chunks
chunk_size = 100000
for start in range(0, total_k2, chunk_size):
    end = min(start + chunk_size, total_k2)
    
    if start % 1000000 == 0:
        print(f"  Progress: {start}/{total_k2} ({100*start//total_k2}%)")
    
    results = check_k2_range(start, end, k2_len)
    
    if results:
        for k1, k2 in results:
            key = k1 + k2
            print(f"\n*** FOUND KEY! ***")
            print(f"k1: {k1.hex()} = {k1}")
            print(f"k2: {k2.hex()} = {k2}")
            print(f"Full key: {key.hex()}")
            
            # Verify
            md5_k1 = md5(k1).digest()
            md5_k2 = md5(k2).digest()
            test_ct = xor_bytes(xor_bytes(known_pt, md5_k1), md5_k2)
            
            if test_ct == known_ct:
                print("✓ Verification SUCCESS!")
                
                # Decrypt flag
                flag_pt = xor_bytes(xor_bytes(flag_ct, md5_k2), md5_k1)
                
                print(f"\nFlag (hex): {flag_pt.hex()}")
                print(f"Flag (bytes): {flag_pt}")
                
                try:
                    flag_text = flag_pt.decode('utf-8', errors='ignore')
                    print(f"Flag (text): {flag_text}")
                    
                    if b'Kaal' in flag_pt:
                        print("\n✓✓✓ FLAG FOUND! ✓✓✓")
                except:
                    pass
                
                exit(0)

print("\nNo key found with k2_len=3")
print("Trying k2_len=4 (this will take longer)...")

k2_len = 4
total_k2 = 256 ** k2_len
chunk_size = 100000

for start in range(0, min(total_k2, 10000000), chunk_size):  # Limit search
    end = min(start + chunk_size, total_k2)
    
    if start % 1000000 == 0:
        print(f"  Progress: {start}/{total_k2} ({100*start//total_k2}%)")
    
    results = check_k2_range(start, end, k2_len)
    
    if results:
        for k1, k2 in results:
            key = k1 + k2
            print(f"\n*** FOUND KEY! ***")
            print(f"k1: {k1.hex()}")
            print(f"k2: {k2.hex()}")
            print(f"Full key: {key.hex()}")
            
            # Decrypt flag
            md5_k1 = md5(k1).digest()
            md5_k2 = md5(k2).digest()
            flag_pt = xor_bytes(xor_bytes(flag_ct, md5_k2), md5_k1)
            
            print(f"\nFlag: {flag_pt}")
            try:
                print(f"Flag text: {flag_pt.decode('utf-8', errors='ignore')}")
            except:
                pass
            
            exit(0)

print("\nSearch incomplete - consider using more compute resources or narrowing key space")
