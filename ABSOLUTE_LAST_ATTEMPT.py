#!/usr/bin/env python3
"""
ABSOLUTE FINAL ATTEMPT
Maybe the solution is simpler - the two numbers we have ARE the answer
Let me try EVERY possible mathematical relationship between them
"""

from Crypto.Util.number import long_to_bytes
import hashlib

comment = 2157869541235478521545895
secret = 83927465839274658392746583

print("="*70)
print("TRYING EVERY POSSIBLE INTERPRETATION")
print("="*70)

# 1. Maybe they need to be concatenated as strings
concat_str = str(comment) + str(secret)
print(f"\n1. Concatenated string: {concat_str}")

# Try as hex
try:
    flag = bytes.fromhex(concat_str)
    print(f"   As hex: {flag}")
except:
    pass

# 2. Maybe XOR them multiple times
print("\n2. XOR operations:")
xor1 = comment ^ secret
print(f"   comment XOR secret: {xor1}")
try:
    print(f"   As bytes: {long_to_bytes(xor1).decode('latin-1', errors='ignore')}")
except:
    pass

# 3. Maybe modulo
print("\n3. Modulo operations:")
if comment > secret:
    mod1 = comment % secret
    print(f"   comment % secret: {mod1}")
    try:
        print(f"   As bytes: {long_to_bytes(mod1).decode('latin-1', errors='ignore')}")
    except:
        pass

# 4. Maybe they're coordinates or indices
print("\n4. As indices/coordinates:")
print(f"   Could be: row={comment}, col={secret}")

# 5. Hash them together
print("\n5. Hash combinations:")
combined = str(comment) + str(secret)
hash_result = hashlib.sha256(combined.encode()).hexdigest()
print(f"   SHA256: {hash_result}")

# Try MD5
md5_result = hashlib.md5(combined.encode()).hexdigest()
print(f"   MD5: {md5_result}")

# 6. Maybe the secret IS the flag when decoded differently
print("\n6. Secret number decoded different ways:")

# As ASCII pairs
secret_str = str(secret)
pairs = [secret_str[i:i+2] for i in range(0, len(secret_str), 2)]
ascii_result = ''
for pair in pairs:
    try:
        val = int(pair)
        if 32 <= val <= 126:
            ascii_result += chr(val)
    except:
        pass

print(f"   Pairs as ASCII: {ascii_result}")
if 'Kaal' in ascii_result or 'kaal' in ascii_result:
    print(f"   *** POTENTIAL FLAG: {ascii_result} ***")

# As triplets
triplets = [secret_str[i:i+3] for i in range(0, len(secret_str), 3)]
ascii_result2 = ''
for trip in triplets:
    try:
        val = int(trip)
        if val < 256:
            ascii_result2 += chr(val)
    except:
        pass

print(f"   Triplets as ASCII: {ascii_result2}")

# 7. Maybe it's base conversion
print("\n7. Base conversions:")
# Treat as base 36, 62, etc
try:
    # Maybe it's encoded in a different base
    secret_hex = hex(secret)[2:]
    print(f"   Secret as hex string: {secret_hex}")
    
    # Try to decode hex string as ASCII
    if len(secret_hex) % 2 == 0:
        decoded = bytes.fromhex(secret_hex)
        print(f"   Hex decoded: {decoded.decode('latin-1', errors='ignore')}")
except:
    pass

# 8. CRITICAL: Maybe the filenames encode something!
print("\n8. Filename analysis:")
print("   soul_stone_1st - position 1")
print("   time_stone_2nd - position 2")  
print("   mind_stone_3rd - position 3")
print("   Maybe: 1st, 2nd, 3rd are indices or ordering hints")

# 9. Try treating the numbers as a cipher key
print("\n9. Using numbers as cipher key:")
# Simple substitution
alphabet = 'abcdefghijklmnopqrstuvwxyz'
key_str = str(secret)[:26]  # First 26 digits
cipher_alphabet = ''.join([alphabet[int(d)] for d in key_str if d.isdigit() and int(d) < 26])
print(f"   Cipher alphabet from secret: {cipher_alphabet}")

# 10. FINAL DESPERATE ATTEMPT - Maybe the flag IS in the secret, just encoded
print("\n10. Deep analysis of secret number:")
secret_bytes = long_to_bytes(secret)
print(f"   Secret as raw bytes: {secret_bytes}")
print(f"   Secret as hex: {secret_bytes.hex()}")

# Check every possible substring
for i in range(len(secret_bytes)):
    for j in range(i+1, min(i+50, len(secret_bytes))):
        substring = secret_bytes[i:j]
        try:
            text = substring.decode('utf-8')
            if 'Kaal{' in text or 'kaal{' in text or 'flag' in text.lower():
                print(f"   *** FOUND AT [{i}:{j}]: {text} ***")
        except:
            pass

print("\n" + "="*70)
print("If nothing worked, the challenge truly needs external RSA parameters")
print("="*70)
