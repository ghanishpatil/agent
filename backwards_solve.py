#!/usr/bin/env python3
"""
Work backwards from the constraint
"""

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# We know: if c2 = "BPCTF{...", then c1 = "SION}d..."
# The '}' suggests c1 might also be a flag or contain braces

# Let's think: what 26-character message starts with "SION}d"?
# Wait - maybe it's backwards or encoded differently

# Let me recalculate more carefully
c2_known = b"BPCTF{"
xor = bytes([c1[i] ^ c2[i] for i in range(len(c1))])

c1_start = bytes([c2_known[i] ^ xor[i] for i in range(len(c2_known))])
print(f"If c2 = 'BPCTF{{...', then c1 starts with: {c1_start}")
print(f"As hex: {c1_start.hex()}")
print(f"As individual bytes: {[hex(b) for b in c1_start]}")
print()

# Hmm, "SION}d" doesn't make sense
# Let me try the opposite - maybe c1 is the flag

print("=== Trying c1 as the flag ===")
c1_known = b"BPCTF{"
c2_start = bytes([c1_known[i] ^ xor[i] for i in range(len(c1_known))])
print(f"If c1 = 'BPCTF{{...', then c2 starts with: {c2_start}")
print()

# Neither makes obvious sense. Let me try a dictionary attack
print("=== Dictionary attack on c1 ===")

# Common 26-character phrases
phrases_26 = [
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "THE QUICK BROWN FOX JUMPS!",
    "NONCE REUSE IS DANGEROUS!!",
    "STREAM CIPHER VULNERABILITY",
    "CRYPTOGRAPHY IS HARD STUFF",
    "NEVER REUSE NONCE IN CRYPTO",
]

for phrase in phrases_26:
    if len(phrase) == 26:
        phrase_bytes = phrase.encode()
        ks = bytes([c1[i] ^ phrase_bytes[i] for i in range(26)])
        dec = bytes([c2[i] ^ ks[i] for i in range(26)])
        
        # Check if printable
        if all(32 <= b < 127 for b in dec):
            print(f"c1 = {phrase}")
            print(f"c2 = {dec.decode()}")
            if b"BPCTF{" in dec:
                print("✓✓✓ FLAG FOUND! ✓✓✓")
            print()

# Let's try generating all possible 26-char messages that start with common words
print("\n=== Trying common starts ===")

starts = ["NONCE", "NEVER", "STREAM", "CRYPTO", "CIPHER", "SECRET", "TIMING"]
ends = [" REUSE!", " MATTERS!", " IS KEY!", " ATTACK!"]

for start in starts:
    for end in ends:
        # Calculate middle padding
        total_len = len(start) + len(end)
        if total_len < 26:
            padding = " " * (26 - total_len)
            phrase = start + padding + end
        elif total_len == 26:
            phrase = start + end
        else:
            continue
            
        phrase_bytes = phrase.encode()
        if len(phrase_bytes) == 26:
            ks = bytes([c1[i] ^ phrase_bytes[i] for i in range(26)])
            dec = bytes([c2[i] ^ ks[i] for i in range(26)])
            
            if all(32 <= b < 127 for b in dec) and b"BPCTF{" in dec:
                print(f"\n✓✓✓ FOUND! ✓✓✓")
                print(f"c1 = {phrase}")
                print(f"c2 = {dec.decode()}")
                print(f"\nFLAG: {dec.decode()}")
                break
