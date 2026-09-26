#!/usr/bin/env python3
"""
Targeted MITM for k1=3 bytes, k2=4 bytes
This is 2^24 * 2^32 = 2^56 total, but MITM reduces it to 2^24 + 2^32
"""

from hashlib import md5
import sys

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

print("Building forward table for k1 (3 bytes)...")
print("This will take ~1 minute and use ~500MB RAM")

forward_table = {}
for b1 in range(256):
    if b1 % 32 == 0:
        print(f"  {b1}/256 ({100*b1//256}%)")
        sys.stdout.flush()
    
    for b2 in range(256):
        for b3 in range(256):
            k1 = bytes([b1, b2, b3])
            md5_k1 = md5(k1).digest()
            intermediate = xor_bytes(known_pt, md5_k1)
            forward_table[intermediate] = k1

print(f"Forward table complete: {len(forward_table)} entries")
print(f"Memory usage: ~{len(forward_table) * 20 // 1024 // 1024}MB")
print()

print("Searching k2 space (4 bytes = 4.3 billion combinations)...")
print("Checking first 50 million to see if we get lucky...")
print()

chunk_size = 1000000
max_check = 50000000  # Check first 50M

for start in range(0, max_check, chunk_size):
    if start % (chunk_size * 5) == 0:
        print(f"  Checked {start:,} / {max_check:,} ({100*start//max_check}%)")
        sys.stdout.flush()
    
    for i in range(start, min(start + chunk_size, max_check)):
        # Convert i to 4-byte key
        k2 = bytes([
            i & 0xFF,
            (i >> 8) & 0xFF,
            (i >> 16) & 0xFF,
            (i >> 24) & 0xFF
        ])
        
        md5_k2 = md5(k2).digest()
        intermediate = xor_bytes(known_ct, md5_k2)
        
        if intermediate in forward_table:
            k1 = forward_table[intermediate]
            key = k1 + k2
            
            print(f"\n{'='*60}")
            print("*** KEY FOUND! ***")
            print(f"{'='*60}")
            print(f"k1 (3 bytes): {k1.hex()} = {list(k1)}")
            print(f"k2 (4 bytes): {k2.hex()} = {list(k2)}")
            print(f"Full key: {key.hex()}")
            print(f"Key as string: {key}")
            print()
            
            # Verify
            md5_k1 = md5(k1).digest()
            md5_k2 = md5(k2).digest()
            test_ct = xor_bytes(xor_bytes(known_pt, md5_k1), md5_k2)
            
            if test_ct == known_ct:
                print("✓ Verification: SUCCESS!")
            else:
                print("✗ Verification: FAILED (collision?)")
                continue
            
            # Decrypt flag
            flag_pt = xor_bytes(xor_bytes(flag_ct, md5_k2), md5_k1)
            
            print()
            print(f"Flag (hex): {flag_pt.hex()}")
            print(f"Flag (bytes): {flag_pt}")
            
            try:
                flag_text = flag_pt.decode('utf-8', errors='ignore')
                print(f"Flag (text): {flag_text}")
                
                if b'Kaal' in flag_pt or b'kaal' in flag_pt:
                    print()
                    print("✓✓✓ FLAG FORMAT MATCHES! ✓✓✓")
            except:
                pass
            
            print(f"{'='*60}")
            sys.exit(0)

print(f"\nChecked {max_check:,} k2 values, no match found.")
print("The key might be in a higher range. Consider:")
print("1. Running this script multiple times with different ranges")
print("2. Using a distributed/parallel approach")
print("3. Checking if there are hints in the diagram or challenge description")
