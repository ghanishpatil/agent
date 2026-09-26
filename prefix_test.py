#!/usr/bin/env python3
"""
Test messages with common prefixes
"""

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# Messages with prefixes
prefix_msgs = [
    "Enc: Two ciphertexts here",  # 26!
    "Msg: Nonce reuse is bad!!!",  # 26!
    "Txt: Stream cipher attack!",  # 26!
    "Key: Never reuse a nonce!!",  # 26!
    "Tip: Nonce must be unique!",  # 26!
    "Hint: XOR reveals secrets!",  # 26!
    "Note: Same nonce is bad!!!",  # 26!
    "Info: Keystream reuse bad!",  # 26!
]

print("=== Testing messages with prefixes ===\n")

for msg in prefix_msgs:
    if len(msg) == 26:
        msg_bytes = msg.encode()
        ks = bytes([c1[i] ^ msg_bytes[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        print(f"c1 = '{msg}'")
        print(f"c2 = {dec}")
        
        if b"BPCTF{" in dec:
            print(f"\n✓✓✓ FLAG FOUND! ✓✓✓")
            print(f"FLAG: {dec.decode()}")
            exit(0)
        
        printable = sum(1 for b in dec if 32 <= b < 127)
        if printable >= 22:
            print(f"  ^ {printable}/26 printable")
        print()

# Since I keep seeing "Enc:" maybe one message literally starts with that
enc_msgs = [
    "Encrypted message number 1",  # 26!
    "Encrypted with same nonce!",  # 26!
    "Encryption using same key!",  # 26!
]

print("=== Testing 'Encrypted' messages ===\n")
for msg in enc_msgs:
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

# Try numbered messages
numbered = [
    "Message 1: Nonce reuse!!!",  # 26!
    "Message 2: Flag is here!!",  # 26!
    "Plaintext 1: Test message",  # 26!
    "Plaintext 2: BPCTF{....}",  # 26!
]

print("=== Testing numbered messages ===\n")
for msg in numbered:
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

# Maybe it's literally describing what it is
literal = [
    "This is the first message",  # 26!
    "This is plaintext number 1",  # 26!
    "First of two ciphertexts!",  # 26!
    "Second message has the flag",  # 27 - too long
]

print("=== Testing literal descriptions ===\n")
for msg in literal:
    if len(msg) <= 26:
        if len(msg) < 26:
            msg = msg + "!" * (26 - len(msg))
        msg = msg[:26]
        
        msg_bytes = msg.encode()
        ks = bytes([c1[i] ^ msg_bytes[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        print(f"c1 = '{msg}'")
        print(f"c2 = {dec}")
        
        if b"BPCTF{" in dec:
            print(f"\n✓✓✓ FLAG: {dec.decode()}")
            exit(0)
        print()
