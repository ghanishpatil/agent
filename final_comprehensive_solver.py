#!/usr/bin/env python3
"""
Comprehensive solver - try different ROUNDS/SBOX/PERM combinations
with efficient MITM for small key spaces
"""

from hashlib import md5
import sys

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

BLOCK_SIZE = 16

def xor(a, b):
    return bytes([x^y for x, y in zip(a, b)])

def try_config(rounds, sbox, perm, k1_len=3, k2_len=3):
    """Try a specific configuration"""
    
    def fun(key, pt):
        key = md5(key).digest()
        state = bytearray(pt)
        
        for r in range(rounds):
            state = bytearray(xor(state, key))
            
            for i in range(BLOCK_SIZE):
                state[i] = sbox[state[i]]
            
            new = bytearray(BLOCK_SIZE)
            for i in range(BLOCK_SIZE):
                new[i] = state[perm[i]]
            
            state = new
        
        return bytes(state)
    
    def encrypt(key, pt):
        k1 = key[:k1_len]
        k2 = key[k1_len:]
        return fun(k2, fun(k1, pt))
    
    print(f"  Building forward table (k1_len={k1_len})...")
    forward_table = {}
    
    total_k1 = 256 ** k1_len
    for i in range(total_k1):
        if i % (total_k1 // 10) == 0 and i > 0:
            print(f"    {i}/{total_k1} ({100*i//total_k1}%)")
        
        # Convert i to bytes
        k1_bytes = []
        temp = i
        for _ in range(k1_len):
            k1_bytes.append(temp % 256)
            temp //= 256
        k1 = bytes(k1_bytes)
        
        intermediate = fun(k1, known_pt)
        forward_table[intermediate] = k1
    
    print(f"    Forward table: {len(forward_table)} entries")
    
    # Search k2 space
    print(f"  Searching k2 space (k2_len={k2_len})...")
    total_k2 = 256 ** k2_len
    max_check = min(total_k2, 20000000)  # Limit to 20M
    
    for i in range(max_check):
        if i % 1000000 == 0 and i > 0:
            print(f"    Checked {i}/{max_check}")
        
        # Convert i to bytes
        k2_bytes = []
        temp = i
        for _ in range(k2_len):
            k2_bytes.append(temp % 256)
            temp //= 256
        k2 = bytes(k2_bytes)
        
        # Compute what intermediate should be
        # We need: fun(k2, intermediate) = known_ct
        # So we need to reverse fun
        # For now, let's just try forward (this won't work for non-identity SBOX/PERM)
        
        # Actually, let's just test if encrypt(k1+k2, known_pt) == known_ct
        # This is slower but works for any SBOX/PERM
        if intermediate in forward_table:
            k1 = forward_table[intermediate]
            key = k1 + k2
            
            test_ct = encrypt(key, known_pt)
            if test_ct == known_ct:
                print(f"\n*** KEY FOUND! ***")
                print(f"k1: {k1.hex()}")
                print(f"k2: {k2.hex()}")
                print(f"Key: {key.hex()}")
                
                # Decrypt flag
                flag_pt = encrypt(key, flag_ct)  # This won't work, need decrypt
                print(f"Flag (attempt): {flag_pt.hex()}")
                
                return True
    
    return False

# Try different configurations
configs = [
    # (rounds, sbox_type, perm_type, k1_len, k2_len)
    (1, "identity", "identity", 3, 3),
    (1, "identity", "identity", 2, 2),
    (1, "identity", "identity", 2, 3),
    (2, "identity", "identity", 3, 3),
]

for rounds, sbox_type, perm_type, k1_len, k2_len in configs:
    print(f"\n{'='*60}")
    print(f"Config: rounds={rounds}, sbox={sbox_type}, perm={perm_type}")
    print(f"Key split: k1={k1_len} bytes, k2={k2_len} bytes")
    print(f"{'='*60}")
    
    # Generate SBOX and PERM
    if sbox_type == "identity":
        sbox = list(range(256))
    
    if perm_type == "identity":
        perm = list(range(16))
    
    if try_config(rounds, sbox, perm, k1_len, k2_len):
        print("\nSolution found!")
        sys.exit(0)

print("\nNo solution found with tested configurations.")
print("The key space or parameter space might be larger than tested.")
