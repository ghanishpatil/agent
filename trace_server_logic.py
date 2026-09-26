#!/usr/bin/env python3
"""
Trace the server logic to understand what triggers the flag
"""

import requests
import hashlib
import time

URL = "http://138.199.163.92:12871"

def create_collision_files():
    """Create MD5 collision files"""
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

def test_server_logic():
    """
    Server responses observed:
    1. "First puppy added 🐶" - First upload in session
    2. "Looks like the same puppy 😏" - Same file (same bytes) uploaded again
    3. "Still not matching 😏" - Different file uploaded
    
    For MD5 collision to be detected, we need:
    - Two DIFFERENT files (different bytes)
    - With SAME MD5 hash
    - Uploaded in the same session
    
    The server should respond with something like "Collision detected!" and give us the flag
    """
    
    file1, file2 = create_collision_files()
    
    print("[*] File properties:")
    print(f"    File1 MD5: {hashlib.md5(file1).hexdigest()}")
    print(f"    File2 MD5: {hashlib.md5(file2).hexdigest()}")
    print(f"    Same MD5: {hashlib.md5(file1).hexdigest() == hashlib.md5(file2).hexdigest()}")
    print(f"    Different bytes: {file1 != file2}")
    
    # The server must be checking:
    # 1. Store first upload's MD5 and content
    # 2. On second upload, check if MD5 matches but content differs
    # 3. If yes -> collision detected -> return flag
    
    print("\n[*] Testing collision detection...")
    session = requests.Session()
    
    # Upload file1
    files1 = {'image': ('img1.png', file1, 'image/png')}
    r1 = session.post(f"{URL}/collision", files=files1)
    
    print(f"\n[Upload 1]")
    print(f"  Response: {r1.text}")
    print(f"  Status: {r1.status_code}")
    
    # Check all headers
    print(f"  Headers:")
    for k, v in r1.headers.items():
        if 'x-' in k.lower() or 'flag' in k.lower():
            print(f"    {k}: {v}")
    
    # Upload file2 (different content, same MD5)
    files2 = {'image': ('img2.png', file2, 'image/png')}
    r2 = session.post(f"{URL}/collision", files=files2)
    
    print(f"\n[Upload 2]")
    print(f"  Response: {r2.text}")
    print(f"  Status: {r2.status_code}")
    
    # Check all headers
    print(f"  Headers:")
    for k, v in r2.headers.items():
        if 'x-' in k.lower() or 'flag' in k.lower():
            print(f"    {k}: {v}")
    
    # Check response body for flag
    if 'Kaal{' in r2.text:
        print(f"\n[!] FLAG IN RESPONSE: {r2.text}")
        return
    
    # Maybe we need to make a third request?
    print(f"\n[*] Trying third upload with file1 again...")
    files3 = {'image': ('img1.png', file1, 'image/png')}
    r3 = session.post(f"{URL}/collision", files=files3)
    print(f"  Response: {r3.text}")
    
    if 'Kaal{' in r3.text:
        print(f"\n[!] FLAG IN RESPONSE: {r3.text}")
        return
    
    # Try GET requests
    print(f"\n[*] Trying GET requests after uploads...")
    for endpoint in ['/', '/collision', '/flag', '/success', '/verify']:
        r = session.get(f"{URL}{endpoint}")
        if 'Kaal{' in r.text:
            print(f"[!] FLAG at {endpoint}: {r.text}")
            return
        elif r.status_code == 200 and endpoint not in ['/', '/collision']:
            print(f"  {endpoint}: {r.status_code} - {r.text[:100]}")
    
    # Check cookies
    print(f"\n[*] Session cookies:")
    for k, v in session.cookies.items():
        print(f"    {k}: {v}")
        if 'kaal{' in v.lower():
            print(f"    [!] FLAG IN COOKIE!")

if __name__ == "__main__":
    print("="*70)
    print("Trace Server Logic")
    print("="*70)
    test_server_logic()
