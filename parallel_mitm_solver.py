#!/usr/bin/env python3
"""
Parallel MITM solver - uses multiprocessing to speed up the search
Focuses on k1=3, k2=3 which is the most likely based on the challenge structure
"""

from hashlib import md5
from multiprocessing import Pool, Manager, cpu_count
import sys

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

def build_forward_table():
    """Build forward table for all 3-byte k1 values"""
    print("Building forward table for k1 (3 bytes)...")
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
    
    print(f"Forward table complete: {len(forward_table)} entries\n")
    return forward_table

def check_k2_chunk(args):
    """Check a chunk of k2 values"""
    start, end, forward_table = args
    
    for i in range(start, end):
        # Convert i to 3-byte k2
        k2 = bytes([
            i & 0xFF,
            (i >> 8) & 0xFF,
            (i >> 16) & 0xFF
        ])
        
        md5_k2 = md5(k2).digest()
        intermediate = xor_bytes(known_ct, md5_k2)
        
        if intermediate in forward_table:
            k1 = forward_table[intermediate]
            return (k1, k2)
    
    return None

if __name__ == '__main__':
    # Build forward table
    forward_table = build_forward_table()
    
    # Search k2 space in parallel
    total_k2 = 256 ** 3  # 16,777,216
    num_processes = cpu_count()
    chunk_size = 100000
    
    print(f"Searching k2 space (3 bytes = {total_k2:,} combinations)")
    print(f"Using {num_processes} processes")
    print()
    
    # Create chunks
    chunks = []
    for start in range(0, total_k2, chunk_size):
        end = min(start + chunk_size, total_k2)
        chunks.append((start, end, forward_table))
    
    # Process in parallel
    with Pool(processes=num_processes) as pool:
        for i, result in enumerate(pool.imap_unordered(check_k2_chunk, chunks)):
            if (i + 1) % 10 == 0:
                progress = (i + 1) * chunk_size
                print(f"  Progress: {progress:,} / {total_k2:,} ({100*progress//total_k2}%)")
                sys.stdout.flush()
            
            if result is not None:
                k1, k2 = result
                key = k1 + k2
                
                print(f"\n{'='*60}")
                print("*** KEY FOUND! ***")
                print(f"{'='*60}")
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
                    print("✗ Verification: FAILED")
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
                        print("\n✓✓✓ FLAG FOUND! ✓✓✓")
                except:
                    pass
                
                print(f"{'='*60}")
                pool.terminate()
                sys.exit(0)
    
    print("\nSearch complete - no key found with k1=3, k2=3")
    print("The key might use a different length split or non-identity SBOX/PERM")
