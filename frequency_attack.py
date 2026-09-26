#!/usr/bin/env python3
"""
Use frequency analysis and common CTF patterns
"""

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

print(f"c1 length: {len(c1)} bytes")
print(f"c2 length: {len(c2)} bytes")
print()

# The flag format is BPCTF{...}
# c2 is 28 bytes, which could fit "BPCTF{" + 21 chars + "}"

# Let's try assuming c1 is a common 26-byte message
# and brute force character by character

def try_message(msg, c1, c2):
    if len(msg) != len(c1):
        return None
    ks = bytes([c1[i] ^ msg[i] for i in range(len(msg))])
    dec = bytes([c2[i] ^ ks[i] for i in range(min(len(ks), len(c2)))])
    return dec

# Let's try messages related to the challenge theme
messages_26 = [
    b"Two ciphertexts, one key",  # 24 + padding
    b"Same nonce, different text",  # 26!
    b"Nonce reused, flag leaked!",  # 26!
    b"XOR attack reveals secret!",  # 26!
]

print("=== Testing themed messages ===\n")
for msg in messages_26:
    if len(msg) == 26:
        dec = try_message(msg, c1, c2)
        if dec:
            print(f"c1 = {msg}")
            print(f"c2 = {dec}")
            if b"BPCTF{" in dec:
                print(f"✓✓✓ FLAG: {dec.decode()}")
                exit(0)
            print()

# Try padding messages to exactly 26
test_msgs = [
    "Two ciphertexts one key",
    "Same nonce different msg",
    "Nonce reused flag leaked",
    "XOR attack reveals flag",
    "Stream cipher nonce flaw",
]

print("=== Testing with padding ===\n")
for msg in test_msgs:
    # Pad to 26
    if len(msg) < 26:
        msg = msg + "!" * (26 - len(msg))
    elif len(msg) > 26:
        msg = msg[:26]
    
    msg_bytes = msg.encode()
    dec = try_message(msg_bytes, c1, c2)
    if dec and all(32 <= b < 127 for b in dec[:15]):
        print(f"c1 = {msg}")
        print(f"c2 = {dec[:28]}")
        if b"BPCTF{" in dec:
            print(f"✓✓✓ FLAG: {dec.decode()}")
            exit(0)
        print()

# Let's try a completely different approach
# Maybe both messages are related to each other
print("\n=== Trying related message pairs ===\n")

pairs = [
    (b"Question: What is a nonce", b"Answer: BPCTF{...}"),
    (b"Hint: Never reuse a nonce", b"Flag: BPCTF{...}"),
]

# Actually, let me try working with what we know
# We know the XOR of the two plaintexts
xor_pt = bytes([c1[i] ^ c2[i] for i in range(len(c1))])

# If we guess one character of p1, we know the corresponding character of p2
# Let's assume p2 (the longer one) is "BPCTF{nonce_reuse_is_bad}"

guesses = [
    b"BPCTF{nonce_reuse_is_bad}",
    b"BPCTF{nonce_reuse_attack}",
    b"BPCTF{stream_cipher_fail}",
    b"BPCTF{xor_plaintext_leak}",
    b"BPCTF{same_key_twice_bad}",
]

print("=== Trying flag guesses for c2 ===\n")
for guess in guesses:
    if len(guess) <= len(c2):
        # Decrypt c1 using this guess for c2
        ks = bytes([c2[i] ^ guess[i] for i in range(len(guess))])
        dec_c1 = bytes([c1[i] ^ ks[i] for i in range(min(len(ks), len(c1)))])
        
        # Check if c1 is readable
        if all(32 <= b < 127 for b in dec_c1):
            print(f"If c2 = {guess}")
            print(f"Then c1 = {dec_c1}")
            print()
