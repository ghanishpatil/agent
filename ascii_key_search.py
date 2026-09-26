#!/usr/bin/env python3
"""
Search for keys using printable ASCII characters
This dramatically reduces the search space
"""

from hashlib import md5
import itertools
import string

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

# Define character sets to try
charsets = {
    "lowercase": string.ascii_lowercase.encode(),
    "uppercase": string.ascii_uppercase.encode(),
    "digits": string.digits.encode(),
    "alphanumeric": (string.ascii_letters + string.digits).encode(),
    "printable": string.printable[:62].encode(),  # Exclude whitespace
}

def test_key(key):
    """Test if a key works"""
    if len(key) < 4:
        return False
    
    k1 = key[:3]
    k2 = key[3:]
    
    md5_k1 = md5(k1).digest()
    md5_k2 = md5(k2).digest()
    
    test_ct = xor_bytes(xor_bytes(known_pt, md5_k1), md5_k2)
    
    if test_ct == known_ct:
        print(f"\n{'='*60}")
        print("*** KEY FOUND! ***")
        print(f"{'='*60}")
        print(f"Key: {key}")
        print(f"Key (hex): {key.hex()}")
        print(f"k1: {k1} (hex: {k1.hex()})")
        print(f"k2: {k2} (hex: {k2.hex()})")
        
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
        return True
    
    return False

# Try different key lengths and character sets
for charset_name, charset in charsets.items():
    print(f"\n=== Trying {charset_name} charset ({len(charset)} chars) ===")
    
    # Try different key lengths
    for total_len in [6, 7, 8]:
        k1_len = 3
        k2_len = total_len - k1_len
        
        total_combinations = len(charset) ** total_len
        print(f"\nKey length: {total_len} (k1={k1_len}, k2={k2_len})")
        print(f"Total combinations: {total_combinations:,}")
        
        if total_combinations > 10000000:
            print("Too many combinations, skipping...")
            continue
        
        count = 0
        for key_tuple in itertools.product(charset, repeat=total_len):
            key = bytes(key_tuple)
            
            if test_key(key):
                exit(0)
            
            count += 1
            if count % 100000 == 0:
                print(f"  Checked {count:,} / {total_combinations:,} ({100*count//total_combinations}%)")

print("\n" + "="*60)
print("ASCII key search complete - no match found")
print("="*60)
print("\nThe key might be:")
print("1. Longer than 8 characters")
print("2. Using non-ASCII bytes")
print("3. Require a different SBOX/PERM/ROUNDS configuration")
