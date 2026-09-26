#!/usr/bin/env python3
"""
MD5 Collision Attack for Kaalchakra
Using known MD5 collision techniques
"""

import requests
import hashlib

TARGET_URL = "http://138.199.163.92:12871/"

def create_md5_collision_files():
    """
    Create two files with the same MD5 hash but different content
    Using the famous MD5 collision prefix technique
    """
    print("="*60)
    print("Creating MD5 Collision Files")
    print("="*60)
    
    # These are the famous MD5 collision blocks discovered by Marc Stevens
    # Two different 128-byte blocks that produce the same MD5 hash
    
    # Collision block 1
    block1 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70"
    )
    
    # Collision block 2 (different content, same MD5)
    block2 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70"
    )
    
    # Create PNG files with these collision blocks
    # PNG header
    png_header = bytes.fromhex("89504e470d0a1a0a")
    
    # Simple PNG structure
    # We'll append the collision blocks as comments or auxiliary chunks
    
    # Create minimal valid PNG files
    # IHDR chunk (image header)
    ihdr = bytes.fromhex(
        "0000000d"  # Length: 13
        "49484452"  # Type: IHDR
        "00000001"  # Width: 1
        "00000001"  # Height: 1
        "08"        # Bit depth: 8
        "02"        # Color type: 2 (RGB)
        "00"        # Compression: 0
        "00"        # Filter: 0
        "00"        # Interlace: 0
        "907753d9"  # CRC
    )
    
    # IDAT chunk (image data) - 1x1 red pixel
    idat = bytes.fromhex(
        "0000000c"  # Length: 12
        "49444154"  # Type: IDAT
        "789c6200010000050001"  # Compressed data
        "0a0a0d0a"  # CRC
    )
    
    # IEND chunk
    iend = bytes.fromhex(
        "00000000"  # Length: 0
        "49454e44"  # Type: IEND
        "ae426082"  # CRC
    )
    
    # Create file 1 with collision block 1
    file1_data = png_header + ihdr + block1 + idat + iend
    
    # Create file 2 with collision block 2
    file2_data = png_header + ihdr + block2 + idat + iend
    
    with open('collision1.png', 'wb') as f:
        f.write(file1_data)
    
    with open('collision2.png', 'wb') as f:
        f.write(file2_data)
    
    # Verify they have the same MD5
    hash1 = hashlib.md5(file1_data).hexdigest()
    hash2 = hashlib.md5(file2_data).hexdigest()
    
    print(f"[+] File 1 MD5: {hash1}")
    print(f"[+] File 2 MD5: {hash2}")
    print(f"[+] Files are different: {file1_data != file2_data}")
    print(f"[+] Hashes match: {hash1 == hash2}")
    
    return 'collision1.png', 'collision2.png'

def upload_collision_files(file1, file2):
    """Upload both collision files"""
    print("\n" + "="*60)
    print("Uploading Collision Files")
    print("="*60)
    
    session = requests.Session()
    
    # Upload first file
    print(f"\n[*] Uploading {file1}...")
    with open(file1, 'rb') as f:
        files = {'image': f}
        resp1 = session.post(TARGET_URL + 'collision', files=files)
    
    print(f"[+] Status: {resp1.status_code}")
    print(f"[+] Response: {resp1.text}")
    
    # Upload second file
    print(f"\n[*] Uploading {file2}...")
    with open(file2, 'rb') as f:
        files = {'image': f}
        resp2 = session.post(TARGET_URL + 'collision', files=files)
    
    print(f"[+] Status: {resp2.status_code}")
    print(f"[+] Response: {resp2.text}")
    
    # Check for flag
    if 'kaal{' in resp1.text.lower():
        print(f"\n[!!!] FLAG IN RESPONSE 1: {resp1.text}")
        return resp1.text
    
    if 'kaal{' in resp2.text.lower():
        print(f"\n[!!!] FLAG IN RESPONSE 2: {resp2.text}")
        return resp2.text
    
    return None

def main():
    print("MD5 Collision Attack")
    print()
    
    # Create collision files
    file1, file2 = create_md5_collision_files()
    
    # Upload them
    result = upload_collision_files(file1, file2)
    
    if result:
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("No flag yet - may need different approach")
        print("="*60)

if __name__ == "__main__":
    main()
