#!/usr/bin/env python3
"""
Use common English text patterns and frequency analysis
"""

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# Load common English words and try to build sensible 26-char messages
# Focus on CTF-related themes

# Let's try messages from common CTF challenge descriptions
ctf_messages = [
    "abcdefghijklmnopqrstuvwxyz",  # alphabet
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # uppercase alphabet
    "0123456789ABCDEFGHIJKLMNOP",  # hex-like
    "Two messages, same nonce!",  # exactly 26!
    "Same key stream, bad idea!",  # exactly 26!
    "Reusing nonces is bad news",  # exactly 26!
]

print("=== Testing CTF-themed messages ===\n")

for msg in ctf_messages:
    if len(msg) == 26:
        msg_bytes = msg.encode()
        ks = bytes([c1[i] ^ msg_bytes[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        print(f"c1 = '{msg}'")
        print(f"c2 = {dec}")
        
        if all(32 <= b < 127 for b in dec):
            print("✓ All printable ASCII!")
            if b"BPCTF{" in dec:
                print(f"\n✓✓✓ FLAG: {dec.decode()}")
                exit(0)
        print()

# Try using rockyou-style common passwords/phrases
common_26 = [
    "password1234567890123456",
    "admin@example.com12345678",
    "Welcome to the CTF event!",
    "Congratulations on solving",
]

print("=== Testing common phrases ===\n")
for msg in common_26:
    if len(msg) == 26:
        msg_bytes = msg.encode()
        ks = bytes([c1[i] ^ msg_bytes[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        if all(32 <= b < 127 for b in dec):
            print(f"c1 = '{msg}'")
            print(f"c2 = {dec.decode()}")
            if b"BPCTF{" in dec:
                print(f"\n✓✓✓ FLAG: {dec.decode()}")
                exit(0)

# Let me try one more thing - what if it's base64 or hex encoded?
print("\n=== Checking for encoding patterns ===")
print(f"c1 hex: {c1.hex()}")
print(f"c2 hex: {c2.hex()}")

# Try treating them as if they might decode differently
import base64
try:
    # Maybe the ciphertexts themselves have a pattern
    xor = bytes([c1[i] ^ c2[i] for i in range(len(c1))])
    print(f"\nXOR pattern: {xor.hex()}")
    print(f"XOR as ASCII (if printable): ", end="")
    for b in xor:
        if 32 <= b < 127:
            print(chr(b), end="")
        else:
            print(f"[{b:02x}]", end="")
    print()
except:
    pass

print("\n\nNo flag found with these attempts.")
print("The challenge might require:")
print("1. A specific plaintext message I haven't guessed")
print("2. Additional context or hints from the challenge")
print("3. A different cryptographic approach")
