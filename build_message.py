#!/usr/bin/env python3
"""
Build full messages from crib results
"""

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# From crib dragging, we saw:
# Pos 5: 'REUSE' -> 'MIS^F' (could be part of MISSION)
# Let's try: c1 = "?????REUSE..." and c2 = "?????MISSION..."

# Try building: c1 = "NONCE REUSE..." (26 chars)
# and c2 should contain "MISSION" or similar

test_messages = [
    b"NONCE REUSE IS THE PROBLEM",  # 26 chars
    b"NONCE REUSE ATTACK IS HERE",  # 26 chars  
    b"NONCE REUSE BREAKS CRYPTO!",  # 26 chars
    b"NEVER REUSE NONCE IN CRYPT",  # 26 chars
]

for msg in test_messages:
    if len(msg) == 26:
        ks = bytes([c1[i] ^ msg[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        print(f"c1 = {msg}")
        print(f"c2 = {dec}")
        
        if all(32 <= b < 127 for b in dec):
            print("✓ All printable!")
            if b"BPCTF{" in dec:
                print(f"✓✓✓ FLAG FOUND: {dec.decode()}")
                exit(0)
        print()

# Let's try messages that would give us "MISSION" at position 5 in c2
# If c1[5:10] = "REUSE", then c2[5:10] should be something
# Let me calculate what c1 should be if c2 contains "MISSION"

print("=== Trying to match MISSION in c2 ===\n")

# Try c2 = "BPCTF{MISSION_..." (but we know BPCTF{ at start doesn't work)
# Maybe c2 = "YOUR MISSION IS BPCTF{...}"

c2_guesses = [
    b"YOUR MISSION IS BPCTF{...}",  # 26 chars
    b"THE MISSION: BPCTF{......}",  # 26 chars
    b"MISSION: BPCTF{...........}",  # 27 chars
]

for guess in c2_guesses:
    if len(guess) <= len(c2):
        # Pad if needed
        if len(guess) < 28:
            guess = guess + b"}" * (28 - len(guess))
        
        ks = bytes([c2[i] ^ guess[i] for i in range(min(len(guess), 26))])
        dec_c1 = bytes([c1[i] ^ ks[i] for i in range(26)])
        
        if all(32 <= b < 127 for b in dec_c1):
            print(f"If c2 = {guess[:28]}")
            print(f"Then c1 = {dec_c1}")
            print()

# Let me try a different approach - use the fact that both are likely English
# Common 26-character English phrases

english_phrases = [
    b"The quick brown fox jumped",
    b"This is a test message!!!",
    b"Cryptography is very hard!",
    b"Security through obscurity",
]

print("=== Trying common English phrases ===\n")
for phrase in english_phrases:
    if len(phrase) == 26:
        ks = bytes([c1[i] ^ phrase[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        if all(32 <= b < 127 for b in dec):
            print(f"c1 = {phrase}")
            print(f"c2 = {dec}")
            if b"BPCTF{" in dec:
                print(f"✓✓✓ FLAG: {dec.decode()}")
                exit(0)
            print()

# Let me try one more thing - what if the messages are related to Valentine's Day?
valentine_msgs = [
    b"LOVE IS COMPLICATED TODAY",  # 26 chars
    b"SYNCHRONIZED LOVE FOREVER!",  # 26 chars
    b"TIMING IS EVERYTHING HERE!",  # 26 chars
]

print("=== Trying Valentine-themed messages ===\n")
for msg in valentine_msgs:
    if len(msg) == 26:
        ks = bytes([c1[i] ^ msg[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        print(f"c1 = {msg}")
        print(f"c2 = {dec}")
        
        if all(32 <= b < 127 for b in dec):
            print("✓ All printable!")
            if b"BPCTF{" in dec:
                print(f"✓✓✓ FLAG: {dec.decode()}")
                exit(0)
        print()
