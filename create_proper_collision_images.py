#!/usr/bin/env python3
"""
Create proper MD5 collision using the bonus image
We need to create two DIFFERENT images that have the SAME MD5
"""

import requests
import hashlib
import struct

URL = "http://138.199.163.92:12871"

def download_bonus_image():
    """Download the bonus image"""
    r = requests.get(f"{URL}/image.png")
    return r.content

def create_collision_with_prefix(prefix_data):
    """
    Create MD5 collision by using chosen-prefix collision technique
    For simplicity, we'll use the known collision blocks and pad the prefix
    """
    
    # MD5 processes data in 64-byte blocks
    # We need to pad the prefix to a multiple of 64 bytes
    
    # Calculate padding needed
    prefix_len = len(prefix_data)
    padding_needed = (64 - (prefix_len % 64)) % 64
    
    # Add padding
    padded_prefix = prefix_data + b'\x00' * padding_needed
    
    # Now append the collision blocks
    collision1_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89
55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70
"""
    
    collision2_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89
55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70
"""
    
    collision1 = bytes.fromhex(collision1_hex.replace('\n', ''))
    collision2 = bytes.fromhex(collision2_hex.replace('\n', ''))
    
    # Create two files
    file1 = padded_prefix + collision1
    file2 = padded_prefix + collision2
    
    return file1, file2

def test_collision():
    """Test the collision"""
    print("[*] Downloading bonus image...")
    bonus_img = download_bonus_image()
    print(f"[+] Bonus image size: {len(bonus_img)} bytes")
    print(f"[+] Bonus image MD5: {hashlib.md5(bonus_img).hexdigest()}")
    
    print("\n[*] Creating collision files with bonus image as prefix...")
    file1, file2 = create_collision_with_prefix(bonus_img)
    
    md5_1 = hashlib.md5(file1).hexdigest()
    md5_2 = hashlib.md5(file2).hexdigest()
    
    print(f"[+] File 1 size: {len(file1)} bytes, MD5: {md5_1}")
    print(f"[+] File 2 size: {len(file2)} bytes, MD5: {md5_2}")
    print(f"[+] Files different: {file1 != file2}")
    print(f"[+] MD5 collision: {md5_1 == md5_2}")
    
    if md5_1 != md5_2:
        print("\n[-] Collision failed! The padding approach doesn't work.")
        print("[*] Let me try using just the collision blocks...")
        return test_simple_collision()
    
    print("\n[*] Uploading collision files...")
    session = requests.Session()
    
    files = {'image': ('img1.png', file1, 'image/png')}
    r1 = session.post(f"{URL}/collision", files=files)
    print(f"[1] {r1.text}")
    
    files = {'image': ('img2.png', file2, 'image/png')}
    r2 = session.post(f"{URL}/collision", files=files)
    print(f"[2] {r2.text}")
    
    if 'Kaal{' in r2.text:
        print(f"\n[!] FLAG FOUND: {r2.text}")
        return True
    
    return False

def test_simple_collision():
    """Test with just the collision blocks"""
    collision1_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89
55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70
"""
    
    collision2_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89
55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70
"""
    
    file1 = bytes.fromhex(collision1_hex.replace('\n', ''))
    file2 = bytes.fromhex(collision2_hex.replace('\n', ''))
    
    md5_1 = hashlib.md5(file1).hexdigest()
    md5_2 = hashlib.md5(file2).hexdigest()
    
    print(f"\n[+] Simple collision MD5_1: {md5_1}")
    print(f"[+] Simple collision MD5_2: {md5_2}")
    print(f"[+] Match: {md5_1 == md5_2}")
    
    print("\n[*] Uploading simple collision files...")
    session = requests.Session()
    
    files = {'image': ('img1.bin', file1, 'image/png')}
    r1 = session.post(f"{URL}/collision", files=files)
    print(f"[1] {r1.text}")
    print(f"[1] All headers:")
    for k, v in r1.headers.items():
        print(f"    {k}: {v}")
    
    files = {'image': ('img2.bin', file2, 'image/png')}
    r2 = session.post(f"{URL}/collision", files=files)
    print(f"[2] {r2.text}")
    print(f"[2] All headers:")
    for k, v in r2.headers.items():
        print(f"    {k}: {v}")
    
    if 'Kaal{' in r2.text:
        print(f"\n[!] FLAG FOUND: {r2.text}")
        return True
    
    # Maybe the flag is in a header?
    for k, v in r2.headers.items():
        if 'kaal{' in str(v).lower():
            print(f"\n[!] FLAG in header {k}: {v}")
            return True
    
    return False

if __name__ == "__main__":
    print("="*70)
    print("Create Proper MD5 Collision Images")
    print("="*70)
    test_collision()
