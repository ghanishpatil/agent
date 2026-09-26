#!/usr/bin/env python3
"""
FINAL BETRAYAL CHALLENGE SOLUTION
Once you crack the password hash, use this script to complete the challenge
"""

import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Known values
USERNAME = "hello"
USERNAME_HASH = "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
PASSWORD_HASH = "707b10ba2d8020957997e4127c99147091087a71"

# The AES key from HTML comment
AES_KEY_B64 = "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="
AES_KEY = base64.b64decode(AES_KEY_B64.replace('-', '+').replace('_', '/'))

# The encrypted token
ENCRYPTED_TOKEN = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

print("="*70)
print("BETRAYAL CHALLENGE - FINAL SOLUTION")
print("="*70)

print("\n[STEP 1] Crack the password hash")
print(f"Hash to crack: {PASSWORD_HASH}")
print("\nUse one of these services:")
print("  1. CrackStation: https://crackstation.net/")
print("  2. Hashes.com: https://hashes.com/en/decrypt/hash")
print("  3. MD5Decrypt: https://md5decrypt.net/en/Sha1/")
print("\nOR download rockyou.txt and run:")
print("  john --format=raw-sha1 --wordlist=rockyou.txt hash.txt")

print("\n" + "="*70)
print("[STEP 2] Once you have the password, enter it here:")
print("="*70)

# Allow user to input the cracked password
password = input("\nEnter the cracked password (or press Enter to skip): ").strip()

if password:
    # Verify the password
    h = hashlib.sha1(password.encode()).hexdigest()
    if h == PASSWORD_HASH:
        print(f"✓ Password verified: {password}")
        
        print("\n" + "="*70)
        print("[STEP 3] Decrypt the encrypted token")
        print("="*70)
        
        # Decode the token
        token_bytes = base64.urlsafe_b64decode(ENCRYPTED_TOKEN + '==')
        print(f"\nToken length: {len(token_bytes)} bytes")
        print(f"AES Key length: {len(AES_KEY)} bytes (AES-256)")
        
        # Try different AES modes
        print("\nTrying AES decryption modes...")
        
        # Mode 1: AES-CBC with IV from token
        try:
            print("\n1. AES-CBC (IV from first 16 bytes):")
            iv = token_bytes[:16]
            ciphertext = token_bytes[16:]
            
            # Pad ciphertext to block size if needed
            if len(ciphertext) % 16 != 0:
                padding_needed = 16 - (len(ciphertext) % 16)
                ciphertext = ciphertext + b'\x00' * padding_needed
            
            cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)
            
            # Try to unpad
            try:
                unpadded = unpad(decrypted, AES.block_size)
                text = unpadded.decode('utf-8', errors='ignore')
            except:
                text = decrypted.decode('utf-8', errors='ignore')
            
            print(f"   Decrypted: {text}")
            
            if 'Kaal{' in text:
                import re
                flags = re.findall(r'Kaal\{[^}]+\}', text)
                for flag in flags:
                    print(f"\n*** FLAG FOUND: {flag} ***")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Mode 2: AES-ECB
        try:
            print("\n2. AES-ECB:")
            # Pad to block size
            padded_token = token_bytes
            if len(padded_token) % 16 != 0:
                padding_needed = 16 - (len(padded_token) % 16)
                padded_token = padded_token + b'\x00' * padding_needed
            
            cipher = AES.new(AES_KEY, AES.MODE_ECB)
            decrypted = cipher.decrypt(padded_token)
            
            try:
                unpadded = unpad(decrypted, AES.block_size)
                text = unpadded.decode('utf-8', errors='ignore')
            except:
                text = decrypted.decode('utf-8', errors='ignore')
            
            print(f"   Decrypted: {text}")
            
            if 'Kaal{' in text:
                import re
                flags = re.findall(r'Kaal\{[^}]+\}', text)
                for flag in flags:
                    print(f"\n*** FLAG FOUND: {flag} ***")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Mode 3: AES-CTR
        try:
            print("\n3. AES-CTR:")
            from Crypto.Util import Counter
            nonce = token_bytes[:16]
            ciphertext = token_bytes[16:]
            
            ctr = Counter.new(128, initial_value=int.from_bytes(nonce, 'big'))
            cipher = AES.new(AES_KEY, AES.MODE_CTR, counter=ctr)
            decrypted = cipher.decrypt(ciphertext)
            text = decrypted.decode('utf-8', errors='ignore')
            
            print(f"   Decrypted: {text}")
            
            if 'Kaal{' in text:
                import re
                flags = re.findall(r'Kaal\{[^}]+\}', text)
                for flag in flags:
                    print(f"\n*** FLAG FOUND: {flag} ***")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Mode 4: Maybe the password itself is used as key?
        try:
            print("\n4. Using password as key:")
            # Derive key from password
            from hashlib import sha256
            pwd_key = sha256(password.encode()).digest()
            
            iv = token_bytes[:16]
            ciphertext = token_bytes[16:]
            
            if len(ciphertext) % 16 != 0:
                padding_needed = 16 - (len(ciphertext) % 16)
                ciphertext = ciphertext + b'\x00' * padding_needed
            
            cipher = AES.new(pwd_key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)
            text = decrypted.decode('utf-8', errors='ignore')
            
            print(f"   Decrypted: {text}")
            
            if 'Kaal{' in text:
                import re
                flags = re.findall(r'Kaal\{[^}]+\}', text)
                for flag in flags:
                    print(f"\n*** FLAG FOUND: {flag} ***")
        except Exception as e:
            print(f"   Error: {e}")
        
    else:
        print(f"✗ Password incorrect. Hash doesn't match.")
        print(f"  Expected: {PASSWORD_HASH}")
        print(f"  Got:      {h}")
else:
    print("\nSkipped. Run this script again once you have the password.")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("\nTo solve this challenge:")
print("1. Crack the SHA-1 hash using CrackStation or rockyou.txt")
print("2. Use the password to decrypt the encrypted token with AES")
print("3. The decrypted token contains the flag or location")
print("\nCredentials:")
print(f"  Username: {USERNAME}")
print(f"  Password: <crack this hash: {PASSWORD_HASH}>")
