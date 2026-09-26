#!/usr/bin/env python3
"""
Try technical crypto messages
"""

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# Technical crypto terms that might be 26 chars
technical_msgs = [
    "AES-CTR mode nonce reuse!",  # 25
    "ChaCha20 stream cipher!!!",  # 25
    "XOR keystream reuse attack",  # 26!
    "Stream cipher nonce reuse!",  # 26!
    "Keystream reuse is bad!!!",  # 25
    "One time pad reused twice!",  # 26!
    "Never reuse the keystream!",  # 26!
    "Reusing keystream is bad!!",  # 26!
    "Two messages same nonce!!!",  # 26!
    "Same nonce different texts",  # 26!
    "Nonce must be used only once",  # 29 - too long
    "Nonce used twice is bad!!!",  # 26!
]

print("=== Testing technical crypto messages ===\n")

for msg in technical_msgs:
    if len(msg) < 26:
        msg = msg + "!" * (26 - len(msg))
    elif len(msg) > 26:
        msg = msg[:26]
    
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
        
        # Check if mostly printable
        printable = sum(1 for b in dec if 32 <= b < 127)
        if printable >= 20:
            print(f"  ^ {printable}/26 printable")
        print()

# Try simpler messages
simple = [
    "abcdefghijklmnopqrstuvwxyz",  # lowercase alphabet
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # uppercase alphabet  
    "zyxwvutsrqponmlkjihgfedcba",  # reverse alphabet
    "ZYXWVUTSRQPONMLKJIHGFEDCBA",  # reverse uppercase
]

print("=== Testing alphabet patterns ===\n")
for msg in simple:
    msg_bytes = msg.encode()
    ks = bytes([c1[i] ^ msg_bytes[i] for i in range(26)])
    dec = bytes([c2[i] ^ ks[i] for i in range(26)])
    
    print(f"c1 = '{msg}'")
    print(f"c2 = {dec}")
    
    if b"BPCTF{" in dec:
        print(f"\n✓✓✓ FLAG: {dec.decode()}")
        exit(0)
    
    printable = sum(1 for b in dec if 32 <= b < 127)
    if printable >= 20:
        print(f"  ^ {printable}/26 printable")
    print()

# Maybe it's a pangram or common test string?
test_strings = [
    "The quick brown fox jumped",  # 26!
    "Pack my box with five dozen",  # 26!
    "How vexingly quick daft zeb",  # 26!
]

print("=== Testing pangrams ===\n")
for msg in test_strings:
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
