#!/usr/bin/env python3
"""
Use real MD5 collision examples
"""

import requests
import hashlib

TARGET_URL = "http://138.199.163.92:12871/"

def create_simple_collision():
    """
    Create a simple collision using the UniColl technique
    This creates two files that differ in one block but have the same MD5
    """
    print("="*60)
    print("Creating Simple MD5 Collision")
    print("="*60)
    
    # Use the classic collision blocks from Marc Stevens' research
    # These are 128-byte blocks that when appended to any prefix,
    # create two files with the same MD5
    
    # Prefix (can be anything)
    prefix = b"This is a puppy image header\n"
    
    # Collision suffix 1
    suffix1 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70"
    )
    
    # Collision suffix 2 (differs in a few bytes)
    suffix2 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70"
    )
    
    # Create two files
    file1 = prefix + suffix1
    file2 = prefix + suffix2
    
    with open('puppy_collision1.bin', 'wb') as f:
        f.write(file1)
    
    with open('puppy_collision2.bin', 'wb') as f:
        f.write(file2)
    
    # Check hashes
    hash1 = hashlib.md5(file1).hexdigest()
    hash2 = hashlib.md5(file2).hexdigest()
    
    print(f"[+] File 1 MD5: {hash1}")
    print(f"[+] File 2 MD5: {hash2}")
    print(f"[+] Files different: {file1 != file2}")
    print(f"[+] Hashes match: {hash1 == hash2}")
    
    if hash1 == hash2:
        print("\n[!!!] SUCCESS - Created collision!")
        return 'puppy_collision1.bin', 'puppy_collision2.bin'
    else:
        print("\n[-] Collision failed")
        return None, None

def test_upload(file1, file2):
    """Test uploading the collision files"""
    if not file1 or not file2:
        return
    
    print("\n" + "="*60)
    print("Testing Upload")
    print("="*60)
    
    session = requests.Session()
    
    # Upload first
    print(f"\n[*] Uploading {file1}...")
    with open(file1, 'rb') as f:
        files = {'image': f}
        resp1 = session.post(TARGET_URL + 'collision', files=files)
    
    print(f"[+] Response: {resp1.text}")
    
    # Upload second
    print(f"\n[*] Uploading {file2}...")
    with open(file2, 'rb') as f:
        files = {'image': f}
        resp2 = session.post(TARGET_URL + 'collision', files=files)
    
    print(f"[+] Response: {resp2.text}")
    
    # Check for flag
    for resp in [resp1, resp2]:
        if 'kaal{' in resp.text.lower():
            import re
            flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
            if flag:
                print(f"\n[!!!] FLAG: {flag.group(0)}")
                return flag.group(0)

def main():
    file1, file2 = create_simple_collision()
    
    if file1 and file2:
        test_upload(file1, file2)
    else:
        print("\n[*] Need to use external MD5 collision tool")
        print("[*] Try: fastcoll, hashclash, or download known collision files")

if __name__ == "__main__":
    main()
