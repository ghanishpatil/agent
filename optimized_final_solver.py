#!/usr/bin/env python3
"""
Highly optimized solver - focuses on most likely scenarios
Uses numpy for speed if available
"""

from hashlib import md5
import sys
import time

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

print("=== Optimized Final Solver ===\n")
print("Testing most likely scenario: k1=3 bytes, k2=3 bytes")
print("Total combinations: 16,777,216 x 16,777,216 = 281 trillion")
print("With MITM: 16.7M + 16.7M = 33.5M operations\n")

# Build forward table
print("Building forward table...")
start = time.time()

forward_table = {}
total_k1 = 256 ** 3

for i in range(total_k1):
    if i % 1000000 == 0:
        elapsed = time.time() - start
        rate = i / elapsed if elapsed > 0 else 0
        print(f"  {i:,}/{total_k1:,} ({100*i//total_k1}%) - {rate:,.0f}/s")
        sys.stdout.flush()
    
    k1 = bytes([
        i & 0xFF,
        (i >> 8) & 0xFF,
        (i >> 16) & 0xFF
    ])
    
    md5_k1 = md5(k1).digest()
    intermediate = xor_bytes(known_pt, md5_k1)
    forward_table[intermediate] = k1

elapsed = time.time() - start
print(f"Forward table complete: {len(forward_table):,} entries in {elapsed:.1f}s\n")

# Search k2 space
print("Searching k2 space...")
start = time.time()

total_k2 = 256 ** 3

for i in range(total_k2):
    if i % 1000000 == 0:
        elapsed = time.time() - start
        rate = i / elapsed if elapsed > 0 else 0
        remaining = (total_k2 - i) / rate if rate > 0 else 0
        print(f"  {i:,}/{total_k2:,} ({100*i//total_k2}%) - {rate:,.0f}/s - ETA: {remaining/60:.1f}min")
        sys.stdout.flush()
    
    k2 = bytes([
        i & 0xFF,
        (i >> 8) & 0xFF,
        (i >> 16) & 0xFF
    ])
    
    md5_k2 = md5(k2).digest()
    intermediate = xor_bytes(known_ct, md5_k2)
    
    if intermediate in forward_table:
        k1 = forward_table[intermediate]
        key = k1 + k2
        
        print(f"\n{'='*70}")
        print("*** KEY FOUND! ***")
        print(f"{'='*70}")
        print(f"k1: {k1.hex()} = {list(k1)}")
        print(f"k2: {k2.hex()} = {list(k2)}")
        print(f"Full key: {key.hex()}")
        print(f"Key as bytes: {key}")
        print()
        
        # Verify
        md5_k1 = md5(k1).digest()
        md5_k2 = md5(k2).digest()
        test_ct = xor_bytes(xor_bytes(known_pt, md5_k1), md5_k2)
        
        if test_ct == known_ct:
            print("✓ Verification: SUCCESS!")
        else:
            print("✗ Verification: FAILED (hash collision?)")
            continue
        
        # Decrypt flag
        flag_pt = xor_bytes(xor_bytes(flag_ct, md5_k2), md5_k1)
        
        print()
        print(f"Flag (hex): {flag_pt.hex()}")
        print(f"Flag (bytes): {flag_pt}")
        
        try:
            flag_text = flag_pt.decode('utf-8', errors='ignore')
            print(f"Flag (text): {flag_text}")
            
            if b'Kaal' in flag_pt:
                print("\n" + "="*70)
                print("✓✓✓ FLAG FOUND! ✓✓✓")
                print("="*70)
        except:
            pass
        
        sys.exit(0)

print("\n\nSearch complete - no key found with k1=3, k2=3")
print("Next step: Try k1=3, k2=4 (will take much longer)")
