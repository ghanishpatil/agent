#!/usr/bin/env python3
"""
Final brute force attempt with systematic approach
"""
import itertools
import string

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# Let me try a smarter approach
# Generate all reasonable 26-character messages programmatically

words = ["NONCE", "REUSE", "IS", "THE", "KEY", "TO", "ATTACK", "STREAM", "CIPHER",
         "CRYPTO", "FLAG", "SECRET", "NEVER", "ALWAYS", "TIMING", "LOVE", "FOREVER",
         "SYNCHRONIZED", "DANGEROUS", "VULNERABILITY", "XOR", "PLAINTEXT", "MISSION",
         "IMPOSSIBLE", "POSSIBLE", "CHALLENGE", "SOLUTION", "ANSWER", "QUESTION"]

print("=== Generating and testing combinations ===\n")

# Try 2-4 word combinations that sum to 26 characters
tested = 0
for num_words in range(2, 5):
    for combo in itertools.combinations(words, num_words):
        # Try different separators
        for sep in [" ", "_", "-", ""]:
            msg = sep.join(combo)
            
            # Pad or truncate to 26
            if len(msg) < 26:
                msg = msg + " " * (26 - len(msg))
            elif len(msg) > 26:
                msg = msg[:26]
            else:
                pass  # exactly 26
            
            if len(msg) == 26:
                msg_bytes = msg.encode()
                ks = bytes([c1[i] ^ msg_bytes[i] for i in range(26)])
                dec = bytes([c2[i] ^ ks[i] for i in range(26)])
                
                tested += 1
                
                # Check if result contains BPCTF{
                if b"BPCTF{" in dec:
                    print(f"\n✓✓✓ FOUND! ✓✓✓")
                    print(f"c1 = '{msg}'")
                    print(f"c2 = {dec}")
                    print(f"\nFLAG: {dec.decode('latin-1')}")
                    exit(0)
                
                # Check if mostly printable
                printable_count = sum(1 for b in dec if 32 <= b < 127)
                if printable_count >= 20:  # At least 20/26 printable
                    print(f"Candidate: c1='{msg[:30]}' -> c2={dec[:15]}...")
        
        if tested % 1000 == 0:
            print(f"Tested {tested} combinations...")

print(f"\nTested {tested} total combinations, no flag found.")
