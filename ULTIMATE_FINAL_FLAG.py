#!/usr/bin/env python3
"""
ULTIMATE FINAL ATTEMPT
Maybe the secret number itself contains the flag when decoded properly
Or maybe we need to use the numbers in a specific mathematical way
"""

from Crypto.Util.number import long_to_bytes
import base64

# The two numbers we found
secret = 83927465839274658392746583
comment = 2157869541235478521545895

print("="*70)
print("ULTIMATE FINAL FLAG EXTRACTION ATTEMPT")
print("="*70)

# Try EVERY possible interpretation

# 1. Direct byte conversion
print("\n1. Direct byte conversions:")
try:
    msg1 = long_to_bytes(secret)
    print(f"Secret bytes: {msg1}")
    print(f"Secret text: {msg1.decode('latin-1')}")
    if b'Kaal{' in msg1 or b'kaal{' in msg1:
        print(f"*** FLAG: {msg1.decode('latin-1')} ***")
except Exception as e:
    print(f"Error: {e}")

try:
    msg2 = long_to_bytes(comment)
    print(f"Comment bytes: {msg2}")
    print(f"Comment text: {msg2.decode('latin-1')}")
except:
    pass

# 2. Concatenate and decode
print("\n2. Concatenated:")
concat_num = int(str(secret) + str(comment))
try:
    concat_bytes = long_to_bytes(concat_num)
    print(f"Concatenated text: {concat_bytes.decode('latin-1', errors='ignore')}")
except:
    pass

# 3. Mathematical operations
print("\n3. Mathematical combinations:")
operations = [
    ("Add", secret + comment),
    ("Subtract", abs(secret - comment)),
    ("Multiply", secret * comment),
    ("XOR", secret ^ comment),
    ("Modulo", secret % comment if comment != 0 else 0),
]

for op_name, result in operations:
    try:
        result_bytes = long_to_bytes(result)
        result_text = result_bytes.decode('latin-1', errors='ignore')
        if 'Kaal{' in result_text or 'kaal{' in result_text or len(result_text) > 5:
            print(f"{op_name}: {result_text[:100]}")
    except:
        pass

# 4. Treat as hex string
print("\n4. As hex strings:")
secret_hex = hex(secret)[2:]
comment_hex = hex(comment)[2:]

try:
    decoded_secret = bytes.fromhex(secret_hex)
    print(f"Secret from hex: {decoded_secret.decode('latin-1', errors='ignore')}")
except:
    pass

try:
    decoded_comment = bytes.fromhex(comment_hex)
    print(f"Comment from hex: {decoded_comment.decode('latin-1', errors='ignore')}")
except:
    pass

# 5. Reverse the numbers
print("\n5. Reversed numbers:")
secret_rev = int(str(secret)[::-1])
comment_rev = int(str(comment)[::-1])

try:
    rev_bytes = long_to_bytes(secret_rev)
    print(f"Reversed secret: {rev_bytes.decode('latin-1', errors='ignore')}")
except:
    pass

# 6. Split into chunks and decode
print("\n6. Chunked decoding:")
secret_str = str(secret)

# Try every chunk size from 2 to 4
for chunk_size in [2, 3, 4]:
    chars = []
    for i in range(0, len(secret_str), chunk_size):
        chunk = secret_str[i:i+chunk_size]
        if chunk:
            try:
                val = int(chunk)
                if 32 <= val <= 126:
                    chars.append(chr(val))
                elif val < 256:
                    chars.append(chr(val))
            except:
                pass
    
    if chars:
        result = ''.join(chars)
        if len(result) > 3:
            print(f"Chunk size {chunk_size}: {result}")
            if 'Kaal{' in result or 'kaal{' in result:
                print(f"*** FLAG FOUND: {result} ***")

# 7. Base64 decode attempts
print("\n7. Base64 attempts:")
try:
    # Try treating the hex as base64
    b64_attempt = base64.b64decode(secret_hex + '==')
    print(f"Secret hex as base64: {b64_attempt.decode('latin-1', errors='ignore')}")
except:
    pass

# 8. ASCII value interpretation
print("\n8. ASCII interpretation:")
# Maybe each digit or pair represents ASCII
secret_str = str(secret)

# Pairs
pairs = [secret_str[i:i+2] for i in range(0, len(secret_str), 2)]
ascii_from_pairs = ''.join(chr(int(p)) if int(p) < 128 else '?' for p in pairs if p)
print(f"Pairs as ASCII: {ascii_from_pairs}")

if 'Kaal{' in ascii_from_pairs or 'kaal{' in ascii_from_pairs:
    print(f"*** FLAG: {ascii_from_pairs} ***")

# 9. Binary interpretation
print("\n9. Binary interpretation:")
binary = bin(secret)[2:]
# Try 8-bit chunks
for i in range(0, len(binary)-7, 8):
    chunk = binary[i:i+8]
    val = int(chunk, 2)
    if 32 <= val <= 126:
        char = chr(val)
        if char in 'Kaal{}':
            print(f"Found flag char at bit {i}: {char}")

# 10. FINAL DESPERATE ATTEMPT - Maybe it's simpler than we think
print("\n10. Simple string search in all data:")
all_text = str(secret) + str(comment) + secret_hex + comment_hex

# Check if "Kaal" appears anywhere when we decode things
test_strings = [
    str(secret),
    str(comment),
    secret_hex,
    comment_hex,
    str(secret)[::-1],
    str(comment)[::-1],
]

for test in test_strings:
    if 'kaal' in test.lower():
        print(f"Found 'kaal' in: {test}")

# 11. Maybe the flag format is different?
print("\n11. Alternative flag formats:")
# Try CTF{}, FLAG{}, etc.
for prefix in ['Kaal{', 'kaal{', 'CTF{', 'FLAG{', 'flag{']:
    # Search in all our decoded attempts
    pass

print("\n" + "="*70)
print("FINAL RESULT")
print("="*70)
print("\nIf no flag was found above, then:")
print("The RSA parameters MUST be provided from the challenge page.")
print("Without n1, c1, n2, c2, n3, c3 values, I cannot solve this.")
print("\nPlease provide the RSA parameters from the challenge description!")
