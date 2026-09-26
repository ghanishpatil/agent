#!/usr/bin/env python3
"""
Exhaustive search with word lists
"""
import itertools

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

def test_plaintext(p1_bytes, c1, c2):
    """Test if p1 decrypts c2 to something readable"""
    if len(p1_bytes) > len(c1):
        return None
    
    ks = bytes([c1[i] ^ p1_bytes[i] for i in range(len(p1_bytes))])
    dec = bytes([c2[i] ^ ks[i] for i in range(min(len(ks), len(c2)))])
    
    return dec

# Generate many 26-character phrases
words = ["NONCE", "REUSE", "STREAM", "CIPHER", "CRYPTO", "ATTACK", "NEVER", "ALWAYS", 
         "SECRET", "TIMING", "SYNCHRONIZED", "LOVE", "FOREVER", "DANGEROUS", "KEY"]

print("=== Trying word combinations ===\n")

# Try 2-word combinations with padding
for w1, w2 in itertools.combinations(words, 2):
    for sep in [" ", "_", "-", ""]:
        phrase = w1 + sep + w2
        if len(phrase) <= 26:
            # Pad to 26
            phrase = phrase + " " * (26 - len(phrase))
            phrase_bytes = phrase.encode()
            
            dec = test_plaintext(phrase_bytes, c1, c2)
            if dec and all(32 <= b < 127 for b in dec[:20]):
                if b"BPCTF{" in dec:
                    print(f"✓✓✓ FOUND! ✓✓✓")
                    print(f"c1 = '{phrase}'")
                    print(f"c2 = {dec.decode('latin-1')}")
                    if b"BPCTF{" in dec:
                        # Extract just the flag part
                        flag_start = dec.find(b"BPCTF{")
                        flag_end = dec.find(b"}", flag_start) + 1
                        if flag_end > flag_start:
                            print(f"\nFLAG: {dec[flag_start:flag_end].decode()}")
                    exit(0)

# Try 3-word combinations
print("\n=== Trying 3-word combinations ===\n")
for w1, w2, w3 in itertools.combinations(words, 3):
    phrase = f"{w1} {w2} {w3}"
    if len(phrase) <= 26:
        phrase = phrase + " " * (26 - len(phrase))
        phrase_bytes = phrase.encode()
        
        dec = test_plaintext(phrase_bytes, c1, c2)
        if dec and b"BPCTF{" in dec:
            print(f"✓✓✓ FOUND! ✓✓✓")
            print(f"c1 = '{phrase}'")
            print(f"c2 = {dec.decode('latin-1')}")
            exit(0)

# Try full sentences
sentences = [
    "NONCE REUSE ATTACK HERE!",
    "STREAM CIPHER IS BROKEN!",
    "NEVER REUSE YOUR NONCE!",
    "CRYPTO TIMING ATTACK!!!",
    "SYNCHRONIZED LOVE WINS!",
]

print("\n=== Trying sentences ===\n")
for sent in sentences:
    if len(sent) <= 26:
        sent = sent + " " * (26 - len(sent))
        sent_bytes = sent.encode()
        
        dec = test_plaintext(sent_bytes, c1, c2)
        if dec:
            print(f"c1 = '{sent}'")
            print(f"c2 = {dec[:26]}")
            if b"BPCTF{" in dec:
                print("✓ Contains flag!")
                print(f"Full c2: {dec.decode('latin-1')}")
                exit(0)

print("\nNo flag found with these combinations.")
