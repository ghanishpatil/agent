#!/usr/bin/env python3
"""
Alternative approach - maybe we don't need the password?
Or maybe the password is derived from the comment/token?
"""

import hashlib
import base64

target_hash = "707b10ba2d8020957997e4127c99147091087a71"
comment_b64 = "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="
encrypted_token = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

print("="*70)
print("ALTERNATIVE APPROACH - DERIVE PASSWORD")
print("="*70)

# Decode comment
comment_bytes = base64.b64decode(comment_b64.replace('-', '+').replace('_', '/'))
print(f"\nComment bytes: {comment_bytes.hex()}")
print(f"Comment length: {len(comment_bytes)}")

# Try various transformations of the comment as password
candidates = []

# 1. Hex string
candidates.append(('comment_hex', comment_bytes.hex()))
candidates.append(('comment_hex_upper', comment_bytes.hex().upper()))

# 2. Base64 variations
candidates.append(('comment_b64', comment_b64))
candidates.append(('comment_b64_no_padding', comment_b64.rstrip('=')))
candidates.append(('comment_b64_no_special', comment_b64.replace('-', '').replace('_', '')))

# 3. First/last N bytes
for n in [4, 8, 16]:
    candidates.append((f'first_{n}_bytes_hex', comment_bytes[:n].hex()))
    candidates.append((f'last_{n}_bytes_hex', comment_bytes[-n:].hex()))
    candidates.append((f'first_{n}_bytes_b64', base64.b64encode(comment_bytes[:n]).decode()))
    candidates.append((f'last_{n}_bytes_b64', base64.b64encode(comment_bytes[-n:]).decode()))

# 4. XOR with known values
known_username = b'hello'
for i in range(len(comment_bytes) - len(known_username) + 1):
    xored = bytes([comment_bytes[i+j] ^ known_username[j] for j in range(len(known_username))])
    candidates.append((f'xor_hello_offset_{i}', xored.hex()))
    try:
        candidates.append((f'xor_hello_offset_{i}_ascii', xored.decode('ascii')))
    except:
        pass

# 5. Token variations
token_bytes = base64.urlsafe_b64decode(encrypted_token + '==')
candidates.append(('token_hex', token_bytes.hex()))
candidates.append(('token_first_8_hex', token_bytes[:8].hex()))
candidates.append(('token_last_8_hex', token_bytes[-8:].hex()))

# 6. Combinations
candidates.append(('hello_comment_hex', 'hello' + comment_bytes.hex()[:16]))
candidates.append(('comment_hello', comment_bytes.hex()[:16] + 'hello'))

print(f"\nTrying {len(candidates)} derived passwords...")

for name, pwd in candidates:
    try:
        h = hashlib.sha1(pwd.encode()).hexdigest()
        if h == target_hash:
            print(f"\n*** PASSWORD FOUND: {pwd} ***")
            print(f"Derivation: {name}")
            print(f"Hash: {h}")
            
            with open('BETRAYAL_PASSWORD.txt', 'w') as f:
                f.write(f"Password: {pwd}\n")
                f.write(f"Derivation: {name}\n")
                f.write(f"Hash: {h}\n")
            
            exit(0)
    except:
        pass

print("\n✗ Password not found through derivation")

# Maybe we need to look at the actual website more carefully
print("\n" + "="*70)
print("ALTERNATIVE THEORY")
print("="*70)
print("""
Maybe the challenge doesn't require cracking the password at all?

Possibilities:
1. The encrypted token can be decrypted WITHOUT logging in
2. There's a bypass or vulnerability in the login
3. The password is provided elsewhere (CTF platform, Discord, etc.)
4. The challenge is broken or password was changed
5. Need to inspect the website's JavaScript more carefully

Let me check if we can decrypt the token directly...
""")

# Try to decrypt token with the comment as key
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    
    key = comment_bytes
    token = token_bytes
    
    print("\nAttempting direct decryption...")
    
    # Try all modes
    modes = [
        ('ECB', AES.MODE_ECB, None),
        ('CBC_iv_from_token', AES.MODE_CBC, token[:16]),
        ('CBC_zero_iv', AES.MODE_CBC, b'\x00' * 16),
    ]
    
    for mode_name, mode, iv in modes:
        try:
            print(f"\n{mode_name}:")
            if iv is None:
                cipher = AES.new(key, mode)
                # Pad token to block size
                padded = token + b'\x00' * (16 - len(token) % 16) if len(token) % 16 != 0 else token
                decrypted = cipher.decrypt(padded)
            else:
                cipher = AES.new(key, mode, iv)
                ciphertext = token[16:] if mode_name == 'CBC_iv_from_token' else token
                # Pad to block size
                padded = ciphertext + b'\x00' * (16 - len(ciphertext) % 16) if len(ciphertext) % 16 != 0 else ciphertext
                decrypted = cipher.decrypt(padded)
            
            # Try to decode
            text = decrypted.decode('utf-8', errors='ignore')
            print(f"  {text[:100]}")
            
            if 'Kaal{' in text:
                import re
                flags = re.findall(r'Kaal\{[^}]+\}', text)
                for flag in flags:
                    print(f"\n*** FLAG FOUND: {flag} ***")
                    exit(0)
        except Exception as e:
            print(f"  Error: {e}")

except ImportError:
    print("\nPyCryptodome not installed")

print("\n✗ Direct decryption failed")
print("\nConclusion: Password cracking is required but password is not in common wordlists")
