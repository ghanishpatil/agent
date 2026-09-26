#!/usr/bin/env python3
"""
Ultimate collision solve - maybe the server checks something specific
"""

import requests
import hashlib

URL = "http://138.199.163.92:12871"

def create_collision_files():
    file1_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89
55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70
"""
    
    file2_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89
55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70
"""
    
    file1 = bytes.fromhex(file1_hex.replace('\n', ''))
    file2 = bytes.fromhex(file2_hex.replace('\n', ''))
    
    return file1, file2

# Maybe the server wants us to send BOTH files in ONE request?
def try_multiple_files_at_once():
    """Try uploading both files in a single request"""
    file1, file2 = create_collision_files()
    
    print("[*] Trying to upload both files in one request...")
    
    files = [
        ('image', ('img1.png', file1, 'image/png')),
        ('image', ('img2.png', file2, 'image/png'))
    ]
    
    r = requests.post(f"{URL}/collision", files=files)
    print(f"  Response: {r.text}")
    print(f"  Status: {r.status_code}")
    
    if 'Kaal{' in r.text:
        print(f"[!] FLAG: {r.text}")
        return True
    
    return False

# Maybe we need to send the MD5 hash as a parameter?
def try_with_md5_parameter():
    """Try sending MD5 as parameter"""
    file1, file2 = create_collision_files()
    md5_hash = hashlib.md5(file1).hexdigest()
    
    print(f"\n[*] Trying with MD5 parameter: {md5_hash}")
    
    session = requests.Session()
    
    # Upload file1 with MD5
    files = {'image': ('img1.png', file1, 'image/png')}
    data = {'md5': md5_hash}
    r1 = session.post(f"{URL}/collision", files=files, data=data)
    print(f"  Upload 1: {r1.text}")
    
    # Upload file2 with same MD5
    files = {'image': ('img2.png', file2, 'image/png')}
    data = {'md5': md5_hash}
    r2 = session.post(f"{URL}/collision", files=files, data=data)
    print(f"  Upload 2: {r2.text}")
    
    if 'Kaal{' in r2.text:
        print(f"[!] FLAG: {r2.text}")
        return True
    
    return False

# Check if there's a /verify endpoint that checks collision
def try_verify_endpoint():
    """Try a verify endpoint"""
    file1, file2 = create_collision_files()
    
    print(f"\n[*] Trying /verify endpoint...")
    
    session = requests.Session()
    
    # Upload both files first
    files = {'image': ('img1.png', file1, 'image/png')}
    session.post(f"{URL}/collision", files=files)
    
    files = {'image': ('img2.png', file2, 'image/png')}
    session.post(f"{URL}/collision", files=files)
    
    # Try verify
    r = session.post(f"{URL}/verify")
    print(f"  Response: {r.status_code} - {r.text[:200]}")
    
    if 'Kaal{' in r.text:
        print(f"[!] FLAG: {r.text}")
        return True
    
    return False

# Maybe the X-Secret IS the flag but needs decoding
def decode_x_secret():
    """The X-Secret might be encoded"""
    file1, _ = create_collision_files()
    
    files = {'image': ('img.png', file1, 'image/png')}
    r = requests.post(f"{URL}/collision", files=files)
    
    secret = r.headers.get('X-Secret')
    prefix = r.headers.get('X-Prefix')
    
    print(f"\n[*] Decoding X-Secret...")
    print(f"  Prefix: {prefix}")
    print(f"  Secret: {secret}")
    
    # The prefix "laak_de43e58e" reversed is "e85e34ed_kaal"
    # Maybe we need to reverse the secret too?
    reversed_secret = secret[::-1]
    print(f"  Reversed secret: {reversed_secret}")
    print(f"  Flag candidate: Kaal{{{reversed_secret}}}")
    
    # Or maybe combine them differently
    # prefix suffix is "de43e58e"
    suffix = prefix.split('_')[1]
    print(f"  Suffix: {suffix}")
    print(f"  Flag candidate: Kaal{{{suffix}}}")

if __name__ == "__main__":
    print("="*70)
    print("Ultimate Collision Solve")
    print("="*70)
    
    if not try_multiple_files_at_once():
        if not try_with_md5_parameter():
            if not try_verify_endpoint():
                decode_x_secret()
