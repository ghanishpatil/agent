#!/usr/bin/env python3
"""
Advanced nonce reuse attack with automated plaintext recovery
"""

nonce = "f39760897597b9b0ffccdfa1"
ciphertext_1 = "e30cd84c2c34838929172f382d8894bbad73f64597341e748a2d"
ciphertext_2 = "f215d456152b8f8f241487d8f035d08e9691b4421818123e7392ada9"

c1 = bytes.fromhex(ciphertext_1)
c2 = bytes.fromhex(ciphertext_2)

# XOR the ciphertexts
xor_result = bytes([c1[i] ^ c2[i] for i in range(min(len(c1), len(c2)))])

print("=== Nonce Reuse Attack ===\n")

# Try common patterns - maybe one message is a hint/description
common_phrases = [
    "The flag is BPCTF{",
    "Your flag: BPCTF{",
    "Flag: BPCTF{",
    "Here is your flag: ",
    "Congratulations! ",
    "Well done! ",
    "nonce reuse attack",
    "stream cipher",
    "This is a test message",
    "Hello world",
]

def try_decrypt(ciphertext, known_plaintext, other_ciphertext):
    """Try to decrypt using known plaintext"""
    if len(known_plaintext) > len(ciphertext):
        return None
    
    # Recover keystream from known plaintext
    keystream = bytes([ciphertext[i] ^ ord(known_plaintext[i]) if isinstance(known_plaintext[i], str) 
                      else ciphertext[i] ^ known_plaintext[i] 
                      for i in range(len(known_plaintext))])
    
    # Decrypt the other ciphertext
    decrypted = bytes([other_ciphertext[i] ^ keystream[i] for i in range(min(len(keystream), len(other_ciphertext)))])
    
    return decrypted

# Try each phrase on both ciphertexts
for phrase in common_phrases:
    phrase_bytes = phrase.encode()
    
    # Try on c1
    result = try_decrypt(c1, phrase_bytes, c2)
    if result and all(32 <= b < 127 for b in result):
        print(f"✓ If c1 = '{phrase}'")
        print(f"  Then c2 = {result}")
        print()
    
    # Try on c2
    result = try_decrypt(c2, phrase_bytes, c1)
    if result and all(32 <= b < 127 for b in result):
        print(f"✓ If c2 = '{phrase}'")
        print(f"  Then c1 = {result}")
        print()

# Try assuming one is the flag format
print("\n=== Trying flag format assumptions ===\n")

# Maybe c2 is longer because it contains the full flag
# Let's try: c1 is a message, c2 is the flag

# Common message lengths and patterns
test_messages = [
    b"nonce reuse is dangerous!",
    b"never reuse a nonce ever!",
    b"stream cipher nonce reuse",
    b"this is a test message!!!",
]

for msg in test_messages:
    if len(msg) <= len(c1):
        keystream = bytes([c1[i] ^ msg[i] for i in range(len(msg))])
        decrypted = bytes([c2[i] ^ keystream[i] for i in range(len(keystream))])
        
        if b"BPCTF{" in decrypted or all(32 <= b < 127 for b in decrypted):
            print(f"If c1 = {msg}")
            print(f"Then c2 = {decrypted}")
            print()

# Try brute force on first character
print("\n=== Brute forcing first characters ===\n")

for c1_char in range(32, 127):
    for c2_char in range(32, 127):
        # Check if this matches the XOR
        if c1_char ^ c2_char == xor_result[0]:
            # Check if either starts with common letters
            if chr(c1_char) in 'BFNSTW' or chr(c2_char) in 'BFNSTW':
                print(f"c1[0] = '{chr(c1_char)}', c2[0] = '{chr(c2_char)}'")
