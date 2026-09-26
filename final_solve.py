#!/usr/bin/env python3
"""
Final solve attempt - try all reasonable combinations
"""
import string

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# XOR them
xor = bytes([c1[i] ^ c2[i] for i in range(len(c1))])

print("XOR of ciphertexts:", xor.hex())
print()

# Try assuming c1 is exactly 26 characters and contains a message
# c2 is 28 characters and contains the flag

# Let's try: "NONCE REUSE IS DANGEROUS!!" (26 chars)
test1 = b"NONCE REUSE IS DANGEROUS!!"
if len(test1) == 26:
    ks = bytes([c1[i] ^ test1[i] for i in range(26)])
    dec = bytes([c2[i] ^ ks[i] for i in range(26)])
    print(f"Test 1: c1 = {test1}")
    print(f"        c2 = {dec}")
    if dec.startswith(b"BPCTF{"):
        print(f"✓ FLAG: {dec.decode()}")
    print()

# Try: "Never reuse a nonce ever!" (26 chars)
test2 = b"Never reuse a nonce ever!"
if len(test2) == 26:
    ks = bytes([c1[i] ^ test2[i] for i in range(26)])
    dec = bytes([c2[i] ^ ks[i] for i in range(26)])
    print(f"Test 2: c1 = {test2}")
    print(f"        c2 = {dec}")
    if dec.startswith(b"BPCTF{"):
        print(f"✓ FLAG: {dec.decode()}")
    print()

# Try: "Stream cipher nonce reuse" (26 chars with space)
test3 = b"Stream cipher nonce reuse"
if len(test3) == 26:
    ks = bytes([c1[i] ^ test3[i] for i in range(26)])
    dec = bytes([c2[i] ^ ks[i] for i in range(26)])
    print(f"Test 3: c1 = {test3}")
    print(f"        c2 = {dec}")
    if dec.startswith(b"BPCTF{"):
        print(f"✓ FLAG: {dec.decode()}")
    print()

# Try building from what we know
# Both seem to start with similar patterns
# Let's try: "SYNCHRONIZATION REQUIRED!!" or similar

tests = [
    b"SYNCHRONIZATION REQUIRED!!",
    b"SYNCHRONIZED LOVE FOREVER!",
    b"TIMING IS EVERYTHING HERE!",
    b"PERFECT TIMING IS THE KEY!",
]

for test in tests:
    if len(test) == 26:
        ks = bytes([c1[i] ^ test[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        if dec.startswith(b"BPCTF{") or all(32 <= b < 127 for b in dec):
            print(f"c1 = {test}")
            print(f"c2 = {dec}")
            if dec.startswith(b"BPCTF{"):
                print(f"✓✓✓ FLAG: {dec.decode()}")
            print()

# Let's try a smarter approach - use the XOR to constrain possibilities
print("\n=== Smart search ===")

# We know: c1[0] XOR c2[0] = 0x11
# Possible: B XOR S = 0x11 (66 XOR 83 = 17 = 0x11) ✓

# Let's assume c2 starts with "BPCTF{"
c2_start = b"BPCTF{"
c1_start = bytes([c2_start[i] ^ xor[i] for i in range(len(c2_start))])
print(f"If c2 starts with 'BPCTF{{', then c1 starts with: {c1_start}")

# Now let's try to guess the rest of c1
# It starts with "SION" + something
# Maybe "SION" is part of a word like "FUSION", "VISION", "MISSION", "PASSION"

prefixes = ["", "FU", "VI", "MIS", "PAS", "PRECI", "DECI", "COLLI"]

for prefix in prefixes:
    guess = (prefix + "SION").encode()
    if len(guess) <= 26:
        # Pad or continue the guess
        # Try common continuations
        continuations = [
            " IS THE KEY",
            " MATTERS",
            " REQUIRED",
            " IS LOVE",
        ]
        
        for cont in continuations:
            full_guess = (prefix + "SION" + cont).encode()
            if len(full_guess) <= 26:
                # Pad to 26
                full_guess = full_guess + b" " * (26 - len(full_guess))
                
                ks = bytes([c1[i] ^ full_guess[i] for i in range(26)])
                dec = bytes([c2[i] ^ ks[i] for i in range(26)])
                
                if dec.startswith(b"BPCTF{{"):
                    print(f"\n✓✓✓ FOUND! ✓✓✓")
                    print(f"c1 = {full_guess}")
                    print(f"c2 = {dec}")
                    print(f"\nFLAG: {dec.decode()}")
