#!/usr/bin/env python3
"""
Try edge cases and special scenarios
"""

from hashlib import md5

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

print("=== Edge Case Solver ===\n")

# Edge Case 1: What if ROUNDS=0? Then fun() returns pt unchanged
print("Edge Case 1: ROUNDS=0 (no encryption)")
if known_pt == known_ct:
    print("  PT == CT, so flag = flag_ct")
    print(f"  Flag: {flag_ct}")
else:
    print("  PT != CT, so ROUNDS != 0\n")

# Edge Case 2: What if the key split is at a different position?
# Maybe it's not key[:3] and key[3:], but something else?
print("Edge Case 2: Different key split positions")

for split_pos in [1, 2, 4, 5, 6, 7, 8]:
    print(f"\n  Trying split at position {split_pos}...")
    
    # Try some simple keys
    for key_len in [split_pos + 1, split_pos + 2, split_pos + 3]:
        if key_len > 10:
            continue
        
        # Try all-zero key
        key = bytes([0] * key_len)
        k1 = key[:split_pos]
        k2 = key[split_pos:]
        
        md5_k1 = md5(k1).digest()
        md5_k2 = md5(k2).digest()
        
        test_ct = xor_bytes(xor_bytes(known_pt, md5_k1), md5_k2)
        
        if test_ct == known_ct:
            print(f"    *** FOUND with all-zero key! ***")
            print(f"    Key: {key.hex()}")
            print(f"    Split: k1={k1.hex()}, k2={k2.hex()}")
            
            flag_pt = xor_bytes(xor_bytes(flag_ct, md5_k2), md5_k1)
            print(f"    Flag: {flag_pt}")
            try:
                print(f"    Flag text: {flag_pt.decode('utf-8', errors='ignore')}")
            except:
                pass
            exit(0)

# Edge Case 3: What if it's single encryption, not double?
print("\n\nEdge Case 3: Single encryption (not double)")
print("  Testing: CT = PT XOR MD5(key)")

for key_len in [1, 2, 3, 4, 5, 6, 8, 16]:
    print(f"\n  Key length: {key_len}")
    
    # Try first 10000 keys
    for i in range(min(256 ** key_len, 10000)):
        key_bytes = []
        temp = i
        for _ in range(key_len):
            key_bytes.append(temp % 256)
            temp //= 256
        key = bytes(key_bytes)
        
        md5_key = md5(key).digest()
        test_ct = xor_bytes(known_pt, md5_key)
        
        if test_ct == known_ct:
            print(f"    *** FOUND! ***")
            print(f"    Key: {key.hex()}")
            
            flag_pt = xor_bytes(flag_ct, md5_key)
            print(f"    Flag: {flag_pt}")
            try:
                print(f"    Flag text: {flag_pt.decode('utf-8', errors='ignore')}")
            except:
                pass
            exit(0)

# Edge Case 4: What if MD5 is applied multiple times?
print("\n\nEdge Case 4: Multiple MD5 applications")
print("  Testing: CT = PT XOR MD5(MD5(key))")

for key_len in [3, 4, 5, 6]:
    print(f"\n  Key length: {key_len}")
    
    for i in range(min(256 ** key_len, 10000)):
        key_bytes = []
        temp = i
        for _ in range(key_len):
            key_bytes.append(temp % 256)
            temp //= 256
        key = bytes(key_bytes)
        
        md5_key = md5(md5(key).digest()).digest()
        test_ct = xor_bytes(known_pt, md5_key)
        
        if test_ct == known_ct:
            print(f"    *** FOUND! ***")
            print(f"    Key: {key.hex()}")
            
            flag_pt = xor_bytes(flag_ct, md5_key)
            print(f"    Flag: {flag_pt}")
            try:
                print(f"    Flag text: {flag_pt.decode('utf-8', errors='ignore')}")
            except:
                pass
            exit(0)

# Edge Case 5: What if the key IS the plaintext or ciphertext?
print("\n\nEdge Case 5: Key derived from PT/CT")

test_keys = [
    known_pt,
    known_ct,
    known_pt[:8],
    known_ct[:8],
    known_pt[:6],
    known_ct[:6],
    xor_bytes(known_pt, known_ct),
]

for key in test_keys:
    if len(key) < 4:
        continue
    
    k1 = key[:3]
    k2 = key[3:]
    
    md5_k1 = md5(k1).digest()
    md5_k2 = md5(k2).digest()
    
    test_ct = xor_bytes(xor_bytes(known_pt, md5_k1), md5_k2)
    
    if test_ct == known_ct:
        print(f"  *** FOUND! ***")
        print(f"  Key: {key.hex()}")
        
        flag_pt = xor_bytes(xor_bytes(flag_ct, md5_k2), md5_k1)
        print(f"  Flag: {flag_pt}")
        try:
            print(f"  Flag text: {flag_pt.decode('utf-8', errors='ignore')}")
        except:
            pass
        exit(0)

print("\n\nNo edge cases matched. The challenge likely requires brute force.")
