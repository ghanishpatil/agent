#!/usr/bin/env python3
"""
Nonce Reuse Attack - Stream Cipher
When the same nonce is used twice, we can XOR the ciphertexts to get plaintext XOR
"""

nonce = "f39760897597b9b0ffccdfa1"
ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

# Convert hex to bytes
c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

print(f"Nonce: {nonce}")
print(f"Ciphertext 1 length: {len(c1)} bytes")
print(f"Ciphertext 2 length: {len(c2)} bytes")
print()

# XOR the two ciphertexts
# c1 = p1 XOR keystream
# c2 = p2 XOR keystream
# c1 XOR c2 = p1 XOR p2

min_len = min(len(c1), len(c2))
xor_result = bytes([c1[i] ^ c2[i] for i in range(min_len)])

print("XOR of ciphertexts (p1 XOR p2):")
print(xor_result.hex())
print()

# Since we know the flag format is BPCTF{...}, let's try to recover the key
# If we know part of plaintext 1, we can recover the keystream
known_plaintext = b"BPCTF{"

print("=== Attempting known plaintext attack ===")
print(f"Known plaintext: {known_plaintext}")
print()

# Try assuming ciphertext_1 starts with "BPCTF{"
keystream_partial = bytes([c1[i] ^ known_plaintext[i] for i in range(len(known_plaintext))])
print(f"Recovered keystream (first {len(known_plaintext)} bytes): {keystream_partial.hex()}")

# Now decrypt ciphertext_2 with this keystream
decrypted_c2_partial = bytes([c2[i] ^ keystream_partial[i] for i in range(len(keystream_partial))])
print(f"Decrypted c2 (first {len(known_plaintext)} bytes): {decrypted_c2_partial}")
print()

# Try assuming ciphertext_2 starts with "BPCTF{"
print("=== Trying c2 as the flag ===")
keystream_partial_2 = bytes([c2[i] ^ known_plaintext[i] for i in range(len(known_plaintext))])
print(f"Recovered keystream (first {len(known_plaintext)} bytes): {keystream_partial_2.hex()}")

# Now decrypt ciphertext_1 with this keystream
decrypted_c1_partial = bytes([c1[i] ^ keystream_partial_2[i] for i in range(len(keystream_partial_2))])
print(f"Decrypted c1 (first {len(known_plaintext)} bytes): {decrypted_c1_partial}")
print()

# Let's try a crib-dragging approach
# Common phrases that might appear
cribs = [
    b"BPCTF{",
    b"flag{",
    b"The flag is",
    b"CTF{",
    b"nonce",
    b"reuse",
    b"stream",
    b"cipher",
]

print("=== Crib dragging ===")
for crib in cribs:
    if len(crib) <= len(c1):
        # Try crib at different positions in c1
        for pos in range(len(c1) - len(crib) + 1):
            keystream = bytes([c1[pos + i] ^ crib[i] for i in range(len(crib))])
            
            # Decrypt c2 at the same position
            if pos + len(crib) <= len(c2):
                decrypted = bytes([c2[pos + i] ^ keystream[i] for i in range(len(crib))])
                
                # Check if result is printable ASCII
                if all(32 <= b < 127 for b in decrypted):
                    print(f"Position {pos}, crib '{crib.decode()}' -> c2: {decrypted}")
