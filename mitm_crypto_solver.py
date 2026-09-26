#!/usr/bin/env python3
"""
Meet-in-the-middle attack for the crypto challenge
The encryption is: E(k1, k2, pt) = fun(k2, fun(k1, pt))
With k1 being 3 bytes and k2 being the rest

Strategy:
1. Build a table of all possible fun(k1, known_pt) for all 3-byte k1 values
2. For each possible k2, compute decrypt_fun(k2, known_ct) and check if it's in the table
3. When we find a match, we have both k1 and k2
"""

from hashlib import md5
from collections import defaultdict
import itertools

BLOCK_SIZE = 16

def xor(a, b):
    return bytes([x^y for x, y in zip(a, b)])

# Since ROUNDS, SBOX, PERM are None, we need to figure out what they should be
# Let's try the simplest case first: ROUNDS=1, identity SBOX and PERM

def try_parameters(rounds, sbox, perm, known_pt, known_ct, flag_ct):
    """Try specific parameter values"""
    
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
    
    def decrypt_fun(key, ct):
        """Reverse the fun operation"""
        key = md5(key).digest()
        
        # Create inverse S-box and permutation
        inv_sbox = [0] * 256
        for i in range(256):
            inv_sbox[sbox[i]] = i
        
        inv_perm = [0] * 16
        for i in range(16):
            inv_perm[perm[i]] = i
        
        state = bytearray(ct)
        
        # Reverse the rounds
        for r in range(rounds - 1, -1, -1):
            # Reverse permutation
            new = bytearray(BLOCK_SIZE)
            for i in range(BLOCK_SIZE):
                new[i] = state[inv_perm[i]]
            state = new
            
            # Reverse S-box
            for i in range(BLOCK_SIZE):
                state[i] = inv_sbox[state[i]]
            
            # Reverse XOR
            state = bytearray(xor(state, key))
        
        return bytes(state)
    
    print(f"Trying: rounds={rounds}, building forward table...")
    
    # Phase 1: Build forward table for all 3-byte k1 values
    # This is 2^24 = 16M entries, manageable
    forward_table = {}
    
    # Try smaller key space first - printable ASCII
    charset = bytes(range(256))  # All bytes
    
    # For 3 bytes, we have 256^3 = 16M combinations
    # Let's try a subset first
    count = 0
    for b1 in range(256):
        if b1 % 16 == 0:
            print(f"  Progress: {b1}/256 ({b1*100//256}%)")
        for b2 in range(256):
            for b3 in range(256):
                k1 = bytes([b1, b2, b3])
                intermediate = fun(k1, known_pt)
                forward_table[intermediate] = k1
                count += 1
    
    print(f"  Built forward table with {len(forward_table)} entries")
    
    # Phase 2: Try all possible k2 values and check for matches
    print("Searching for k2 match...")
    
    # k2 can be various lengths, let's try common ones
    for k2_len in [3, 4, 5, 8, 13, 16]:
        print(f"  Trying k2 length: {k2_len}")
        
        # For longer keys, we need to be smarter
        if k2_len <= 3:
            # Brute force small keys
            for k2_bytes in itertools.product(range(256), repeat=k2_len):
                k2 = bytes(k2_bytes)
                intermediate = decrypt_fun(k2, known_ct)
                
                if intermediate in forward_table:
                    k1 = forward_table[intermediate]
                    key = k1 + k2
                    
                    print(f"\n*** FOUND KEY! ***")
                    print(f"k1: {k1.hex()}")
                    print(f"k2: {k2.hex()}")
                    print(f"Full key: {key.hex()}")
                    
                    # Verify
                    test_ct = fun(k2, fun(k1, known_pt))
                    if test_ct == known_ct:
                        print("Verification: SUCCESS!")
                        
                        # Decrypt flag
                        flag_intermediate = decrypt_fun(k2, flag_ct)
                        flag_pt = decrypt_fun(k1, flag_intermediate)
                        
                        print(f"\nFlag plaintext (hex): {flag_pt.hex()}")
                        try:
                            flag_text = flag_pt.decode('utf-8', errors='ignore')
                            print(f"Flag text: {flag_text}")
                        except:
                            print(f"Flag bytes: {flag_pt}")
                        
                        return True
        else:
            # For longer keys, try common patterns
            test_k2s = []
            
            # Try printable ASCII
            for c in b'abcdefghijklmnopqrstuvwxyz0123456789':
                test_k2s.append(bytes([c] * k2_len))
            
            # Try sequential
            test_k2s.append(bytes(range(k2_len)))
            test_k2s.append(bytes(range(k2_len, 0, -1)))
            
            for k2 in test_k2s:
                intermediate = decrypt_fun(k2, known_ct)
                
                if intermediate in forward_table:
                    k1 = forward_table[intermediate]
                    key = k1 + k2
                    
                    print(f"\n*** FOUND KEY! ***")
                    print(f"k1: {k1.hex()}")
                    print(f"k2: {k2.hex()}")
                    print(f"Full key: {key.hex()}")
                    
                    # Verify
                    test_ct = fun(k2, fun(k1, known_pt))
                    if test_ct == known_ct:
                        print("Verification: SUCCESS!")
                        
                        # Decrypt flag
                        flag_intermediate = decrypt_fun(k2, flag_ct)
                        flag_pt = decrypt_fun(k1, flag_intermediate)
                        
                        print(f"\nFlag plaintext (hex): {flag_pt.hex()}")
                        try:
                            flag_text = flag_pt.decode('utf-8', errors='ignore')
                            print(f"Flag text: {flag_text}")
                        except:
                            print(f"Flag bytes: {flag_pt}")
                        
                        return True
    
    return False

# Load known pair
known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

print("Known plaintext:", known_pt.hex())
print("Known ciphertext:", known_ct.hex())
print("Flag ciphertext:", flag_ct.hex())
print()

# Try simple parameters first
for rounds in [1, 2]:
    # Identity SBOX and PERM
    sbox = list(range(256))
    perm = list(range(16))
    
    if try_parameters(rounds, sbox, perm, known_pt, known_ct, flag_ct):
        exit(0)

print("\nNo solution found with simple parameters.")
