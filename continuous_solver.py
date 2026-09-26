#!/usr/bin/env python3
"""
Continuous solver - runs until key is found
Saves progress and can be resumed
"""

from hashlib import md5
import sys
import time
import json
import os

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

PROGRESS_FILE = "crypto_progress.json"

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

def load_progress():
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"last_k2": 0, "k1_len": 3, "k2_len": 4}

def save_progress(data):
    """Save progress to file"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(data, f)

def main():
    progress = load_progress()
    k1_len = progress["k1_len"]
    k2_len = progress["k2_len"]
    start_k2 = progress["last_k2"]
    
    print(f"Configuration: k1={k1_len} bytes, k2={k2_len} bytes")
    print(f"Resuming from k2={start_k2}")
    print()
    
    # Build forward table
    print("Building forward table...")
    start_time = time.time()
    
    forward_table = {}
    total_k1 = 256 ** k1_len
    
    for i in range(total_k1):
        if i % (total_k1 // 20) == 0:
            elapsed = time.time() - start_time
            print(f"  {i}/{total_k1} ({100*i//total_k1}%) - {elapsed:.1f}s")
        
        k1_bytes = []
        temp = i
        for _ in range(k1_len):
            k1_bytes.append(temp % 256)
            temp //= 256
        k1 = bytes(k1_bytes)
        
        md5_k1 = md5(k1).digest()
        intermediate = xor_bytes(known_pt, md5_k1)
        forward_table[intermediate] = k1
    
    elapsed = time.time() - start_time
    print(f"Forward table complete: {len(forward_table)} entries in {elapsed:.1f}s")
    print()
    
    # Search k2 space
    total_k2 = 256 ** k2_len
    print(f"Searching k2 space: {total_k2:,} combinations")
    print(f"Starting from: {start_k2:,}")
    print()
    
    start_time = time.time()
    last_save = time.time()
    
    for i in range(start_k2, total_k2):
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
            key = k1 + k2
            
            print(f"\n{'='*60}")
            print("*** KEY FOUND! ***")
            print(f"{'='*60}")
            print(f"k1: {k1.hex()} = {list(k1)}")
            print(f"k2: {k2.hex()} = {list(k2)}")
            print(f"Full key: {key.hex()}")
            print()
            
            # Verify
            md5_k1 = md5(k1).digest()
            md5_k2 = md5(k2).digest()
            test_ct = xor_bytes(xor_bytes(known_pt, md5_k1), md5_k2)
            
            if test_ct == known_ct:
                print("✓ Verification: SUCCESS!")
                
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
                
                # Clean up progress file
                if os.path.exists(PROGRESS_FILE):
                    os.remove(PROGRESS_FILE)
                
                return True
        
        # Progress reporting and saving
        if i % 1000000 == 0 and i > start_k2:
            elapsed = time.time() - start_time
            rate = (i - start_k2) / elapsed
            remaining = (total_k2 - i) / rate if rate > 0 else 0
            
            print(f"  {i:,} / {total_k2:,} ({100*i//total_k2}%) - "
                  f"Rate: {rate:,.0f}/s - ETA: {remaining/3600:.1f}h")
            sys.stdout.flush()
        
        # Save progress every 5 minutes
        if time.time() - last_save > 300:
            progress["last_k2"] = i
            save_progress(progress)
            last_save = time.time()
            print(f"  [Progress saved at k2={i:,}]")
    
    print("\nSearch complete - no key found")
    return False

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print("Progress has been saved. Run again to resume.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
