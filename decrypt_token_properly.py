#!/usr/bin/env python3
"""
Properly decrypt the token using the key from the comment
The comment "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8=" is 32 bytes when decoded
This is perfect for AES-256
"""

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# The key from the HTML comment
key_b64 = "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="
key = base64.b64decode(key_b64.replace('-', '+').replace('_', '/'))

print(f"Key length: {len(key)} bytes")
print(f"Key hex: {key.hex()}")

# The encrypted token
encrypted_token = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

# Decode the token (URL-safe base64)
encrypted_data = base64.urlsafe_b64decode(encrypted_token + '==')

print(f"\nEncrypted data length: {len(encrypted_data)} bytes")
print(f"Encrypted hex: {encrypted_data.hex()[:100]}...")

# Try different AES modes
print("\n" + "="*70)
print("TRYING DIFFERENT AES MODES")
print("="*70)

# 1. AES-ECB (no IV needed)
print("\n1. AES-ECB:")
try:
    cipher = AES.new(key, AES.MODE_ECB)
    # Pad to block size
    padded_len = (len(encrypted_data) // 16) * 16
    decrypted = cipher.decrypt(encrypted_data[:padded_len])
    print(f"   Decrypted: {decrypted}")
    print(f"   As text: {decrypted.decode('utf-8', errors='ignore')}")
    
    if b'Kaal{' in decrypted:
        print(f"\n   *** FLAG: {decrypted.decode('utf-8', errors='ignore')} ***")
except Exception as e:
    print(f"   Error: {e}")

# 2. AES-CBC with IV from first 16 bytes
print("\n2. AES-CBC (IV from first 16 bytes):")
try:
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
    print(f"   Decrypted: {decrypted}")
    print(f"   As text: {decrypted.decode('utf-8', errors='ignore')}")
    
    if b'Kaal{' in decrypted:
        print(f"\n   *** FLAG: {decrypted.decode('utf-8', errors='ignore')} ***")
except Exception as e:
    print(f"   Error: {e}")

# 3. AES-CBC with zero IV
print("\n3. AES-CBC (zero IV):")
try:
    iv = b'\x00' * 16
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_len = (len(encrypted_data) // 16) * 16
    decrypted = cipher.decrypt(encrypted_data[:padded_len])
    print(f"   Decrypted: {decrypted}")
    print(f"   As text: {decrypted.decode('utf-8', errors='ignore')}")
    
    if b'Kaal{' in decrypted:
        print(f"\n   *** FLAG: {decrypted.decode('utf-8', errors='ignore')} ***")
except Exception as e:
    print(f"   Error: {e}")

# 4. AES-CTR
print("\n4. AES-CTR:")
try:
    from Crypto.Util import Counter
    # Use first 8 bytes as nonce
    nonce = encrypted_data[:8]
    ciphertext = encrypted_data[8:]
    
    ctr = Counter.new(64, prefix=nonce, initial_value=0)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    decrypted = cipher.decrypt(ciphertext)
    print(f"   Decrypted: {decrypted}")
    print(f"   As text: {decrypted.decode('utf-8', errors='ignore')}")
    
    if b'Kaal{' in decrypted:
        print(f"\n   *** FLAG: {decrypted.decode('utf-8', errors='ignore')} ***")
except Exception as e:
    print(f"   Error: {e}")

# 5. Maybe it's XOR encryption?
print("\n5. XOR with key:")
try:
    decrypted = bytes([encrypted_data[i] ^ key[i % len(key)] for i in range(len(encrypted_data))])
    print(f"   Decrypted: {decrypted[:100]}")
    print(f"   As text: {decrypted.decode('utf-8', errors='ignore')}")
    
    if b'Kaal{' in decrypted:
        print(f"\n   *** FLAG: {decrypted.decode('utf-8', errors='ignore')} ***")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*70)
print("If none worked, the token might need to be used differently")
print("="*70)
