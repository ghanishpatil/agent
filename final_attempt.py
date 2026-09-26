#!/usr/bin/env python3
"""
Final systematic attempt with more variations
"""

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# Try messages with numbers and special characters
messages = [
    "Nonce=f39760897597b9b0ff",  # Using the actual nonce!
    "nonce=f39760897597b9b0ff",
    "NONCE=F39760897597B9B0FF",
    "f39760897597b9b0ffccdfa1!!",
    "Two texts encrypted once!",
    "Encrypted with same nonce!",
    "Challenge: Nonce Reuse!!!",
    "CTF Challenge 2024/2025!!",
    "BreachPoint CTF Challenge!",
    "BREACHPOINT CTF 2025 FLAG",
    "Made with love by ATLEE!!",  # From the challenge description!
    "Made with <3 by ATLEE!!!!",
    "Love is in the air today!",
    "Valentine CTF Challenge!!",
]

print("=== Testing challenge-specific messages ===\n")

for msg in messages:
    if len(msg) <= 26:
        # Pad to 26
        msg = msg + " " * (26 - len(msg))
        msg = msg[:26]
        
        msg_bytes = msg.encode()
        ks = bytes([c1[i] ^ msg_bytes[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        # Check if contains flag
        if b"BPCTF{" in dec:
            print(f"✓✓✓ FOUND! ✓✓✓")
            print(f"c1 = '{msg}'")
            print(f"c2 = {dec}")
            print(f"\nFLAG: {dec.decode()}")
            exit(0)
        
        # Check if mostly printable
        printable = sum(1 for b in dec if 32 <= b < 127)
        if printable >= 22:
            print(f"c1 = '{msg}'")
            print(f"c2 = {dec} (printable: {printable}/26)")
            print()

print("Still searching...")

# Try with the actual nonce value in different formats
nonce_msgs = [
    "f39760897597b9b0ffccdfa1",  # exact nonce (24 chars, need +2)
    "f39760897597b9b0ffccdfa1!",  # 25 chars
    "f39760897597b9b0ffccdfa1!!",  # 26 chars!
]

print("\n=== Using actual nonce value ===\n")
for msg in nonce_msgs:
    if len(msg) == 26:
        msg_bytes = msg.encode()
        ks = bytes([c1[i] ^ msg_bytes[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        print(f"c1 = '{msg}'")
        print(f"c2 = {dec}")
        
        if b"BPCTF{" in dec:
            print(f"\n✓✓✓ FLAG: {dec.decode()}")
            exit(0)
        print()

print("\nNo flag found. The plaintext might be something unexpected.")
