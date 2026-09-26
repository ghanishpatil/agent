#!/usr/bin/env python3
"""
Automated crib dragging with extensive word list
"""
import string

ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# Generate a comprehensive word list
words = [
    "THE", "FLAG", "IS", "BPCTF", "NONCE", "REUSE", "ATTACK", "STREAM", "CIPHER",
    "CRYPTO", "KEY", "SECRET", "NEVER", "ALWAYS", "TIMING", "SYNCHRONIZED", "LOVE",
    "FOREVER", "DANGEROUS", "VULNERABILITY", "XOR", "PLAINTEXT", "CIPHERTEXT",
    "ENCRYPTION", "DECRYPTION", "SECURITY", "CHALLENGE", "CTF", "CAPTURE", "BREACHPOINT",
    "TWO", "ONE", "SAME", "DIFFERENT", "LEAKED", "REVEALED", "HIDDEN", "FOUND",
]

def test_crib(crib, pos, c_from, c_to):
    """Test a crib at a position"""
    if pos + len(crib) > len(c_from):
        return None
    
    # Recover keystream
    ks = bytes([c_from[pos + i] ^ crib[i] for i in range(len(crib))])
    
    # Decrypt other ciphertext
    if pos + len(ks) > len(c_to):
        return None
    
    dec = bytes([c_to[pos + i] ^ ks[i] for i in range(len(ks))])
    
    # Check if printable
    if all(32 <= b < 127 for b in dec):
        return dec
    return None

print("=== Comprehensive crib dragging ===\n")

# Try all words at all positions on both ciphertexts
found_cribs = []

for word in words:
    word_bytes = word.encode()
    
    # Try on c1 -> decrypt c2
    for pos in range(len(c1) - len(word_bytes) + 1):
        result = test_crib(word_bytes, pos, c1, c2)
        if result:
            found_cribs.append((pos, word, result.decode('latin-1'), "c1->c2"))
    
    # Try on c2 -> decrypt c1
    for pos in range(len(c2) - len(word_bytes) + 1):
        result = test_crib(word_bytes, pos, c2, c1)
        if result:
            found_cribs.append((pos, word, result.decode('latin-1'), "c2->c1"))

# Print interesting results
print("Found cribs that produce printable text:\n")
for pos, crib, result, direction in found_cribs:
    if len(result) >= 4:  # Only show substantial results
        print(f"Pos {pos:2d} | {direction} | '{crib:15s}' -> '{result}'")

# Now try to build full messages from successful cribs
print("\n=== Building full messages ===\n")

# Look for cribs that might be at position 0
start_cribs = [c for c in found_cribs if c[0] == 0]
if start_cribs:
    print("Cribs at position 0:")
    for pos, crib, result, direction in start_cribs:
        print(f"  {direction}: '{crib}' -> '{result}'")

# Try building a message character by character
# Start with common first letters
print("\n=== Character-by-character recovery ===\n")

# We know c1 is 26 bytes, c2 is 28 bytes
# Let's try to recover c1 by assuming c2 contains "BPCTF{"

c2_guess = bytearray(b"BPCTF{" + b"?" * 22)  # 28 bytes total

# We can recover first 6 bytes of c1
xor_result = bytes([c1[i] ^ c2[i] for i in range(len(c1))])
c1_start = bytes([c2_guess[i] ^ xor_result[i] for i in range(6)])
print(f"If c2 starts with 'BPCTF{{', c1 starts with: {c1_start} ({c1_start.hex()})")

# Now let's try common words that could follow
# c1 might be: "SION..." which could be part of "MISSION", "PASSION", "FUSION", etc.

# But wait - let me check if those bytes make sense
# 0x53 = 'S', 0x49 = 'I', 0x4F = 'O', 0x4E = 'N', 0x7F = DEL (not printable!), 0x64 = 'd'

print("\\nThe 5th byte (0x7F) is not printable, so c2 probably doesn't start with 'BPCTF{'")
print("Let's try c1 starting with 'BPCTF{' instead...")

c1_guess = b"BPCTF{"
c2_start = bytes([c1_guess[i] ^ xor_result[i] for i in range(6)])
print(f"If c1 starts with 'BPCTF{{', c2 starts with: {c2_start} ({c2_start.hex()})")
print(f"As string: {c2_start.decode('latin-1')}")

# Same issue! So neither starts with "BPCTF{"?
# Let me reconsider...

print("\n=== Maybe the flag is embedded, not at the start? ===\n")

# Try "BPCTF{" at different positions in c2
for pos in range(len(c2) - 6):
    crib = b"BPCTF{"
    result = test_crib(crib, pos, c2, c1)
    if result:
        print(f"Position {pos}: If c2[{pos}:{pos+6}] = 'BPCTF{{', then c1[{pos}:{pos+6}] = '{result}'")
