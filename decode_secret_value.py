#!/usr/bin/env python3
"""
The X-Secret might need to be decoded or transformed
"Time traveler" - maybe it's about time-based encoding?
"Lost in time echoes" - maybe reverse or shift?
"""

import hashlib
import base64
import requests

URL = "http://138.199.163.92:12871"

def get_secret():
    """Get the X-Secret header"""
    collision1_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89
55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70
"""
    
    file1 = bytes.fromhex(collision1_hex.replace('\n', ''))
    
    files = {'image': ('img.png', file1, 'image/png')}
    r = requests.post(f"{URL}/collision", files=files)
    
    return r.headers.get('X-Prefix'), r.headers.get('X-Secret')

def try_decodings(secret):
    """Try different ways to decode the secret"""
    print(f"[*] Original secret: {secret}")
    print(f"[*] Length: {len(secret)}")
    
    # Try 1: Reverse
    print(f"\n[1] Reversed: {secret[::-1]}")
    
    # Try 2: Hex decode
    try:
        hex_decoded = bytes.fromhex(secret).decode('utf-8', errors='ignore')
        print(f"\n[2] Hex decoded: {hex_decoded}")
        if 'Kaal{' in hex_decoded:
            print(f"    [!] FLAG FOUND!")
    except:
        print(f"\n[2] Not valid hex")
    
    # Try 3: Base64 decode
    try:
        b64_decoded = base64.b64decode(secret).decode('utf-8', errors='ignore')
        print(f"\n[3] Base64 decoded: {b64_decoded}")
        if 'Kaal{' in b64_decoded:
            print(f"    [!] FLAG FOUND!")
    except:
        print(f"\n[3] Not valid base64")
    
    # Try 4: ROT13
    import codecs
    rot13 = codecs.encode(secret, 'rot13')
    print(f"\n[4] ROT13: {rot13}")
    
    # Try 5: Caesar shifts
    print(f"\n[5] Caesar shifts:")
    for shift in [1, 3, 5, 7, 13]:
        shifted = ''.join(chr((ord(c) - ord('a') + shift) % 26 + ord('a')) if 'a' <= c <= 'z' 
                         else chr((ord(c) - ord('A') + shift) % 26 + ord('A')) if 'A' <= c <= 'Z'
                         else chr((ord(c) - ord('0') + shift) % 10 + ord('0')) if '0' <= c <= '9'
                         else c for c in secret)
        print(f"    Shift {shift}: {shifted[:50]}...")
    
    # Try 6: MD5 of secret
    md5_secret = hashlib.md5(secret.encode()).hexdigest()
    print(f"\n[6] MD5 of secret: {md5_secret}")
    print(f"    Flag candidate: Kaal{{{md5_secret}}}")
    
    # Try 7: SHA1 of secret
    sha1_secret = hashlib.sha1(secret.encode()).hexdigest()
    print(f"\n[7] SHA1 of secret: {sha1_secret}")
    print(f"    Flag candidate: Kaal{{{sha1_secret}}}")
    
    # Try 8: The secret AS IS is the flag content
    print(f"\n[8] Direct flag: Kaal{{{secret}}}")
    
    # Try 9: Split by common separators
    print(f"\n[9] Analyzing structure:")
    print(f"    Contains numbers: {any(c.isdigit() for c in secret)}")
    print(f"    Contains letters: {any(c.isalpha() for c in secret)}")
    print(f"    Alphanumeric only: {secret.isalnum()}")
    
    # Try 10: Check if it's a Flask session secret or similar
    print(f"\n[10] Trying as Flask session secret...")
    # The secret looks like it could be a session secret
    # Format: 38h4vg6s45ch1lr19x4pe18s55r2kh1lx5331mh1mc5656w0
    # This looks like it could be hex or a custom encoding

def check_if_flag_works(flag):
    """Check if a flag candidate works"""
    # We can't really verify without submitting, but we can check format
    if flag.startswith('Kaal{') and flag.endswith('}') and len(flag) > 10:
        print(f"\n[*] Valid flag format: {flag}")
        return True
    return False

if __name__ == "__main__":
    print("="*70)
    print("Decode X-Secret Value")
    print("="*70)
    
    prefix, secret = get_secret()
    print(f"\n[+] X-Prefix: {prefix}")
    print(f"[+] X-Secret: {secret}")
    
    if secret:
        try_decodings(secret)
        
        # The most likely flag based on the pattern
        print(f"\n" + "="*70)
        print(f"MOST LIKELY FLAG:")
        print(f"="*70)
        print(f"Kaal{{{secret}}}")
