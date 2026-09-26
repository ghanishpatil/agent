#!/usr/bin/env python3
"""
Since we know username=hello but not the password,
let's see if we can bypass or if there's another way.

Looking at the JavaScript, after successful login it just shows an alert.
But maybe there's more that happens - let's check the page source more carefully.
"""

import hashlib
import re

# Read the HTML
with open('betrayal_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("="*70)
print("ANALYZING LOGIN LOGIC")
print("="*70)

# Extract the JavaScript
js_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if js_match:
    js_code = js_match.group(1)
    print("\nJavaScript Code:")
    print(js_code)
    
    # Look for what happens after successful login
    print("\n" + "="*70)
    print("AFTER SUCCESSFUL LOGIN")
    print("="*70)
    
    # Find the success block
    success_match = re.search(r"if\(u === '.*?' && p === '.*?'\)\s*\{(.*?)\}", js_code, re.DOTALL)
    if success_match:
        success_code = success_match.group(1)
        print("\nSuccess code:")
        print(success_code)
        
        # It just shows an alert and removes attempts
        # But maybe there's something in the encrypted token that gets used?

# The encrypted token from the challenge description
encrypted_token = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

# The comment/key
comment = "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="

print("\n" + "="*70)
print("THINKING ABOUT THE CHALLENGE")
print("="*70)

print("""
The challenge says:
- Employee betrayed and stole data
- Data copied to external storage devices (hard disks)
- Hard disks are hidden
- We have: encrypted text and website link
- Need to: identify location of storage devices and recover data

The website is just a login page. After login, it shows "Login successful Welcome Admin"
But the REAL challenge is to decrypt the encrypted token to find the location!

The encrypted token is probably encrypted with the AES key from the comment.
But we need the correct password to "unlock" the ability to decrypt it.

OR... maybe we don't need to login at all?
Maybe we can decrypt the token directly with the key from the comment?
""")

import base64

# Try to decrypt the token with the key
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    
    # Decode the key
    key = base64.b64decode(comment.replace('-', '+').replace('_', '/'))
    print(f"\nKey (hex): {key.hex()}")
    print(f"Key length: {len(key)} bytes")
    
    # Decode the token
    token_bytes = base64.urlsafe_b64decode(encrypted_token + '==')
    print(f"\nToken length: {len(token_bytes)} bytes")
    print(f"Token (hex): {token_bytes.hex()[:100]}...")
    
    # Try different AES modes
    print("\n" + "="*70)
    print("TRYING AES DECRYPTION")
    print("="*70)
    
    # Mode 1: ECB
    print("\n1. AES-ECB:")
    try:
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(token_bytes)
        print(f"   Raw: {decrypted.hex()}")
        print(f"   Text: {decrypted.decode('utf-8', errors='ignore')}")
        
        # Try to unpad
        try:
            unpadded = unpad(decrypted, AES.block_size)
            print(f"   Unpadded: {unpadded}")
            if b'Kaal{' in unpadded:
                print(f"\n*** FLAG: {unpadded.decode()} ***")
        except:
            pass
    except Exception as e:
        print(f"   Error: {e}")
    
    # Mode 2: CBC with IV from token
    print("\n2. AES-CBC (IV from token):")
    try:
        iv = token_bytes[:16]
        ciphertext = token_bytes[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        print(f"   Raw: {decrypted.hex()}")
        print(f"   Text: {decrypted.decode('utf-8', errors='ignore')}")
        
        try:
            unpadded = unpad(decrypted, AES.block_size)
            print(f"   Unpadded: {unpadded}")
            if b'Kaal{' in unpadded:
                print(f"\n*** FLAG: {unpadded.decode()} ***")
        except:
            pass
    except Exception as e:
        print(f"   Error: {e}")
    
    # Mode 3: CTR
    print("\n3. AES-CTR:")
    try:
        from Crypto.Util import Counter
        ctr = Counter.new(128, initial_value=int.from_bytes(token_bytes[:16], 'big'))
        cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
        decrypted = cipher.decrypt(token_bytes[16:])
        print(f"   Text: {decrypted.decode('utf-8', errors='ignore')}")
        if b'Kaal{' in decrypted:
            print(f"\n*** FLAG: {decrypted.decode()} ***")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Mode 4: GCM (if there's a tag)
    print("\n4. AES-GCM:")
    try:
        nonce = token_bytes[:16]
        ciphertext = token_bytes[16:-16]
        tag = token_bytes[-16:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        print(f"   Text: {decrypted.decode('utf-8', errors='ignore')}")
        if b'Kaal{' in decrypted:
            print(f"\n*** FLAG: {decrypted.decode()} ***")
    except Exception as e:
        print(f"   Error: {e}")

except ImportError:
    print("\nPyCryptodome not installed")
except Exception as e:
    print(f"\nError: {e}")

print("\nDone")
