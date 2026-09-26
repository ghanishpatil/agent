#!/usr/bin/env python3
"""
Final desperate attempt - try keys based on challenge hints
Challenge name: CnK3cCB
Author: dhruvaaaaa
"""

from hashlib import md5
import string

known_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
known_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

def test_key(key):
    if len(key) < 4:
        return None
    
    k1 = key[:3]
    k2 = key[3:]
    
    md5_k1 = md5(k1).digest()
    md5_k2 = md5(k2).digest()
    
    test_ct = xor_bytes(xor_bytes(known_pt, md5_k1), md5_k2)
    
    if test_ct == known_ct:
        flag_pt = xor_bytes(xor_bytes(flag_ct, md5_k2), md5_k1)
        return flag_pt
    
    return None

print("=== Final Desperate Solver ===\n")

# Hints from challenge
hints = [
    b"CnK3cCB",
    b"cnk3ccb",
    b"CNK3CCB",
    b"dhruva",
    b"dhruvaaaaa",
    b"DHRUVA",
    b"crypto",
    b"CRYPTO",
    b"cipher",
    b"CIPHER",
    b"kaal",
    b"Kaal",
    b"KAAL",
    b"300",  # Points
    b"medium",
    b"MEDIUM",
    # Hex interpretations
    b"\x0c\x0e\x03",  # CnK3cCB might encode something
]

# Try hints as keys
print("Trying hint-based keys...")
for hint in hints:
    if len(hint) < 4:
        continue
    
    # Try as-is
    flag = test_key(hint)
    if flag:
        print(f"\n*** FOUND! ***")
        print(f"Key: {hint}")
        print(f"Key (hex): {hint.hex()}")
        print(f"Flag: {flag}")
        try:
            print(f"Flag text: {flag.decode('utf-8', errors='ignore')}")
        except:
            pass
        exit(0)
    
    # Try with padding
    for pad_len in [6, 7, 8, 16]:
        if len(hint) >= pad_len:
            continue
        
        # Pad with zeros
        padded = hint + b'\x00' * (pad_len - len(hint))
        flag = test_key(padded)
        if flag:
            print(f"\n*** FOUND! ***")
            print(f"Key: {padded}")
            print(f"Key (hex): {padded.hex()}")
            print(f"Flag: {flag}")
            try:
                print(f"Flag text: {flag.decode('utf-8', errors='ignore')}")
            except:
                pass
            exit(0)
        
        # Pad with spaces
        padded = hint + b' ' * (pad_len - len(hint))
        flag = test_key(padded)
        if flag:
            print(f"\n*** FOUND! ***")
            print(f"Key: {padded}")
            print(f"Key (hex): {padded.hex()}")
            print(f"Flag: {flag}")
            try:
                print(f"Flag text: {flag.decode('utf-8', errors='ignore')}")
            except:
                pass
            exit(0)

print("Hint-based keys didn't work\n")

# Try numeric keys (like PINs or years)
print("Trying numeric patterns...")
for year in range(2000, 2027):
    key = str(year).encode()
    
    # Try different lengths
    for extra in [b"", b"00", b"000", b"123", b"456", b"789"]:
        test = key + extra
        if len(test) < 4:
            continue
        
        flag = test_key(test)
        if flag:
            print(f"\n*** FOUND! ***")
            print(f"Key: {test}")
            print(f"Flag: {flag}")
            try:
                print(f"Flag text: {flag.decode('utf-8', errors='ignore')}")
            except:
                pass
            exit(0)

# Try sequential bytes
print("\nTrying sequential patterns...")
for start in range(256):
    for length in [6, 7, 8]:
        key = bytes([(start + i) % 256 for i in range(length)])
        flag = test_key(key)
        if flag:
            print(f"\n*** FOUND! ***")
            print(f"Key: {key.hex()}")
            print(f"Flag: {flag}")
            try:
                print(f"Flag text: {flag.decode('utf-8', errors='ignore')}")
            except:
                pass
            exit(0)

# Try repeating patterns
print("\nTrying repeating patterns...")
for byte_val in range(256):
    if byte_val % 32 == 0:
        print(f"  {byte_val}/256")
    
    for length in [6, 7, 8]:
        key = bytes([byte_val] * length)
        flag = test_key(key)
        if flag:
            print(f"\n*** FOUND! ***")
            print(f"Key: {key.hex()}")
            print(f"Flag: {flag}")
            try:
                print(f"Flag text: {flag.decode('utf-8', errors='ignore')}")
            except:
                pass
            exit(0)

print("\n\nNo simple pattern found.")
print("This challenge requires significant computational resources.")
print("Estimated time for full k1=3, k2=4 search: 10-20 hours on single core")
print("\nRecommendation: Use the continuous_solver.py with multiple instances")
print("or consider cloud computing resources.")
