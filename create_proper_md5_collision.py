#!/usr/bin/env python3
"""
Create proper MD5 collision files
Using the technique where we append collision blocks to a common prefix
"""

import requests
import hashlib
import struct

URL = "http://138.199.163.92:12871"

def create_collision_files():
    """
    Create two files with same MD5 but different content
    Using known MD5 collision technique
    """
    
    # Common prefix - this will be the same for both files
    # We'll use a minimal valid PNG structure
    prefix = bytes.fromhex("89504e470d0a1a0a")  # PNG signature
    
    # These are collision blocks from the famous MD5 collision
    # They differ in a few bytes but produce the same MD5 when appended to the same prefix
    collision1 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70"
    )
    
    collision2 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70"
    )
    
    # Create files: prefix + collision block + suffix
    suffix = b"\x00" * 64  # Padding
    
    file1 = prefix + collision1 + suffix
    file2 = prefix + collision2 + suffix
    
    # Save files
    with open("puppy1.bin", "wb") as f:
        f.write(file1)
    
    with open("puppy2.bin", "wb") as f:
        f.write(file2)
    
    # Verify
    md5_1 = hashlib.md5(file1).hexdigest()
    md5_2 = hashlib.md5(file2).hexdigest()
    
    print(f"[+] File 1 MD5: {md5_1}")
    print(f"[+] File 2 MD5: {md5_2}")
    print(f"[+] Files different: {file1 != file2}")
    print(f"[+] MD5 match: {md5_1 == md5_2}")
    
    return md5_1 == md5_2

def test_collision():
    """Test the collision with the server"""
    print("\n[*] Creating collision files...")
    if not create_collision_files():
        print("[-] Failed to create collision!")
        return
    
    print("\n[*] Testing with server...")
    
    # Upload first file
    with open("puppy1.bin", "rb") as f:
        files = {'image': ('puppy1.png', f, 'image/png')}
        r1 = requests.post(f"{URL}/collision", files=files)
    print(f"[+] Upload 1: {r1.text}")
    
    # Upload second file
    with open("puppy2.bin", "rb") as f:
        files = {'image': ('puppy2.png', f, 'image/png')}
        r2 = requests.post(f"{URL}/collision", files=files)
    print(f"[+] Upload 2: {r2.text}")
    
    if 'Kaal{' in r2.text:
        print(f"\n[!] FLAG: {r2.text}")

if __name__ == "__main__":
    print("="*70)
    print("MD5 Collision Generator")
    print("="*70)
    test_collision()
