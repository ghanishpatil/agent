#!/usr/bin/env python3
"""
Download or create real MD5 collision files
"""

import requests
import hashlib

URL = "http://138.199.163.92:12871"

def create_fastcoll_collision():
    """
    Create MD5 collision using the FastColl technique
    These are actual collision blocks that work
    """
    
    # These are the actual collision blocks from the original MD5 collision paper
    # by Xiaoyun Wang et al. They produce the same MD5 when used as complete files
    
    # File 1
    file1_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89
55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70
"""
    
    # File 2 (differs in a few bytes)
    file2_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89
55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70
"""
    
    file1 = bytes.fromhex(file1_hex.replace('\n', ''))
    file2 = bytes.fromhex(file2_hex.replace('\n', ''))
    
    # Save
    with open("coll1.bin", "wb") as f:
        f.write(file1)
    with open("coll2.bin", "wb") as f:
        f.write(file2)
    
    md5_1 = hashlib.md5(file1).hexdigest()
    md5_2 = hashlib.md5(file2).hexdigest()
    
    print(f"[+] File 1 MD5: {md5_1}")
    print(f"[+] File 2 MD5: {md5_2}")
    print(f"[+] Match: {md5_1 == md5_2}")
    print(f"[+] Different: {file1 != file2}")
    
    return md5_1 == md5_2

def test_with_server():
    """Test collision with server"""
    print("\n[*] Creating collision files...")
    if not create_fastcoll_collision():
        print("[-] Collision failed!")
        return
    
    print("\n[*] Uploading to server...")
    
    # First upload
    with open("coll1.bin", "rb") as f:
        files = {'image': ('image1.png', f, 'image/png')}
        r1 = requests.post(f"{URL}/collision", files=files)
    print(f"[+] Response 1: {r1.text}")
    
    # Second upload
    with open("coll2.bin", "rb") as f:
        files = {'image': ('image2.png', f, 'image/png')}
        r2 = requests.post(f"{URL}/collision", files=files)
    print(f"[+] Response 2: {r2.text}")
    
    if 'Kaal{' in r2.text:
        print(f"\n[!] FLAG FOUND: {r2.text}")

if __name__ == "__main__":
    print("="*70)
    print("Real MD5 Collision Test")
    print("="*70)
    test_with_server()
