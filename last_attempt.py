#!/usr/bin/env python3
"""
Last systematic attempt - famous crypto examples
"""

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# Famous crypto examples and quotes
famous_crypto = [
    "alice and bob communicate",  # 26!
    "eve is eavesdropping here",  # 26!
    "mallory attacks the system",  # 27 - too long
    "caesar cipher is too weak",  # 26!
    "enigma machine was cracked",  # 26!
    "public key cryptography!!!",  # 26!
    "diffie hellman key exchange",  # 28 - too long
]

print("=== Testing famous crypto references ===\n")

for msg in famous_crypto:
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
        print()

# Try messages about the challenge itself
meta = [
    "this challenge uses xor!!!",  # 26!
    "xor ciphertexts together!!",  # 26!
    "crib dragging attack works",  # 26!
    "known plaintext attack!!!",  # 25
]

print("=== Testing meta messages ===\n")
for msg in meta:
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

# Try simple English sentences
simple_english = [
    "i love cryptography a lot!",  # 26!
    "security is very important",  # 26!
    "never trust user input data",  # 26!
    "always validate your inputs",  # 26!
]

print("=== Testing simple English ===\n")
for msg in simple_english:
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

# One more try - maybe it's literally "something familiar"
literal_familiar = [
    "something familiar to you",  # 26!
    "you know this already!!!",  # 24
    "this should be familiar!!",  # 25
    "familiar plaintext message",  # 26!
]

print("=== Testing 'familiar' literally ===\n")
for msg in literal_familiar:
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

print("\n" + "="*50)
print("Unable to find the flag through automated guessing.")
print("This challenge requires either:")
print("1. Additional context/hints from the challenge platform")
print("2. A specific plaintext that I haven't guessed")
print("3. Manual crib-dragging with more context")
print("="*50)
