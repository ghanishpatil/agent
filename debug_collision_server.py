#!/usr/bin/env python3
"""
Debug the collision server behavior
"""

import requests
import hashlib
import time

URL = "http://138.199.163.92:12871"

def create_collision_files():
    """Create the collision files"""
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

def test_different_scenarios():
    """Test different upload scenarios"""
    file1, file2 = create_collision_files()
    
    md5_hash = hashlib.md5(file1).hexdigest()
    print(f"[+] Both files MD5: {md5_hash}")
    print(f"[+] Files are different: {file1 != file2}")
    
    # Test 1: Upload file1 twice
    print("\n" + "="*70)
    print("Test 1: Upload same file twice")
    print("="*70)
    session1 = requests.Session()
    
    files = {'image': ('puppy.png', file1, 'image/png')}
    r1 = session1.post(f"{URL}/collision", files=files)
    print(f"[+] Upload 1: {r1.text}")
    
    files = {'image': ('puppy.png', file1, 'image/png')}
    r2 = session1.post(f"{URL}/collision", files=files)
    print(f"[+] Upload 2: {r2.text}")
    
    # Test 2: Upload file1 then file2 (collision)
    print("\n" + "="*70)
    print("Test 2: Upload collision files (file1 then file2)")
    print("="*70)
    session2 = requests.Session()
    
    files = {'image': ('puppy1.png', file1, 'image/png')}
    r1 = session2.post(f"{URL}/collision", files=files)
    print(f"[+] Upload file1: {r1.text}")
    print(f"[+] Status: {r1.status_code}")
    print(f"[+] Headers: {dict(r1.headers)}")
    
    files = {'image': ('puppy2.png', file2, 'image/png')}
    r2 = session2.post(f"{URL}/collision", files=files)
    print(f"[+] Upload file2: {r2.text}")
    print(f"[+] Status: {r2.status_code}")
    
    if 'Kaal{' in r2.text:
        print(f"\n[!] FLAG: {r2.text}")
    
    # Test 3: Upload file2 then file1 (reverse order)
    print("\n" + "="*70)
    print("Test 3: Upload collision files (file2 then file1)")
    print("="*70)
    session3 = requests.Session()
    
    files = {'image': ('puppy2.png', file2, 'image/png')}
    r1 = session3.post(f"{URL}/collision", files=files)
    print(f"[+] Upload file2: {r1.text}")
    
    files = {'image': ('puppy1.png', file1, 'image/png')}
    r2 = session3.post(f"{URL}/collision", files=files)
    print(f"[+] Upload file1: {r2.text}")
    
    if 'Kaal{' in r2.text:
        print(f"\n[!] FLAG: {r2.text}")
    
    # Test 4: Check if there's a reset endpoint
    print("\n" + "="*70)
    print("Test 4: Check for reset or other endpoints")
    print("="*70)
    
    for endpoint in ['/reset', '/clear', '/flag', '/admin']:
        try:
            r = requests.get(f"{URL}{endpoint}")
            if r.status_code != 404:
                print(f"[+] {endpoint}: {r.status_code} - {r.text[:100]}")
        except:
            pass

if __name__ == "__main__":
    print("="*70)
    print("Debug Collision Server")
    print("="*70)
    test_different_scenarios()
