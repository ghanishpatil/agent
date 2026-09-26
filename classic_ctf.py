#!/usr/bin/env python3
"""
Try classic CTF and crypto test messages
"""

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# Classic test messages
classic = [
    "attack at dawn on tuesday!",  # 26!
    "meet me at the park today!",  # 26!
    "the password is qwerty123!",  # 26!
    "all your base belong to us",  # 26!
    "hello world this is a test",  # 26!
    "testing one two three four",  # 26!
    "lorem ipsum dolor sit amet",  # 26!
    "now is the time for action",  # 26!
    "send reinforcements quickly",  # 27 - too long
]

print("=== Testing classic messages ===\n")

for msg in classic:
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
            print(f"\n✓✓✓ FLAG FOUND! ✓✓✓")
            print(f"FLAG: {dec.decode()}")
            exit(0)
        
        printable = sum(1 for b in dec if 32 <= b < 127)
        if printable >= 22:
            print(f"  ^ {printable}/26 printable")
        print()

# Try with all lowercase
lowercase = [
    "two ciphertexts one nonce",  # 26!
    "nonce reuse vulnerability",  # 26!
    "stream cipher attack here",  # 26!
    "xor two ciphertexts to win",  # 26!
]

print("=== Testing lowercase messages ===\n")
for msg in lowercase:
    if len(msg) == 26:
        msg_bytes = msg.encode()
        ks = bytes([c1[i] ^ msg_bytes[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        print(f"c1 = '{msg}'")
        print(f"c2 = {dec}")
        
        if b"BPCTF{" in dec:
            print(f"\n✓✓✓ FLAG: {dec.decode()}")
            exit(0)
        
        printable = sum(1 for b in dec if 32 <= b < 127)
        if printable >= 22:
            print(f"  ^ {printable}/26 printable")
        print()

# Maybe it's a quote or saying
quotes = [
    "practice makes perfect!!!",  # 25
    "knowledge is power today!",  # 25
    "time is money save it now",  # 26!
    "better late than never!!!",  # 25
]

print("=== Testing quotes/sayings ===\n")
for msg in quotes:
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

# Try simple repeated patterns
patterns = [
    "A" * 26,
    "B" * 26,
    "AB" * 13,
    "ABC" * 8 + "AB",  # 26 chars
    "0123456789" * 2 + "012345",  # 26 chars
]

print("=== Testing patterns ===\n")
for msg in patterns:
    msg_bytes = msg.encode()
    ks = bytes([c1[i] ^ msg_bytes[i] for i in range(26)])
    dec = bytes([c2[i] ^ ks[i] for i in range(26)])
    
    print(f"c1 = '{msg[:20]}...'")
    print(f"c2 = {dec}")
    
    if b"BPCTF{" in dec:
        print(f"\n✓✓✓ FLAG: {dec.decode()}")
        exit(0)
    print()
