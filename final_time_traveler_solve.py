#!/usr/bin/env python3
"""
Final solution for Time Traveler challenge

The solution:
1. Upload MD5 collision files
2. Check response headers for X-Secret
3. The flag is Kaal{X-Secret value}
"""

import requests
import hashlib

URL = "http://138.199.163.92:12871"

def create_collision_files():
    """Create MD5 collision files"""
    # These are the famous MD5 collision blocks
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

def solve():
    """Solve the challenge"""
    print("[*] Creating MD5 collision files...")
    file1, file2 = create_collision_files()
    
    md5_1 = hashlib.md5(file1).hexdigest()
    md5_2 = hashlib.md5(file2).hexdigest()
    
    print(f"[+] File 1 MD5: {md5_1}")
    print(f"[+] File 2 MD5: {md5_2}")
    print(f"[+] MD5 Collision: {md5_1 == md5_2}")
    print(f"[+] Files Different: {file1 != file2}")
    
    print("\n[*] Uploading first collision file...")
    files = {'image': ('puppy1.png', file1, 'image/png')}
    r1 = requests.post(f"{URL}/collision", files=files)
    
    print(f"[+] Response: {r1.text}")
    print(f"[+] Status: {r1.status_code}")
    
    # Check headers
    if 'X-Secret' in r1.headers:
        secret = r1.headers['X-Secret']
        prefix = r1.headers.get('X-Prefix', '')
        
        print(f"\n[+] Found X-Prefix: {prefix}")
        print(f"[+] Found X-Secret: {secret}")
        
        # The flag is constructed from the secret
        flag = f"Kaal{{{secret}}}"
        
        print(f"\n{'='*70}")
        print(f"[!] FLAG FOUND!")
        print(f"{'='*70}")
        print(f"{flag}")
        print(f"{'='*70}")
        
        return flag
    else:
        print("[-] No X-Secret header found")
        print(f"[*] Headers: {dict(r1.headers)}")
    
    return None

if __name__ == "__main__":
    print("="*70)
    print("Time Traveler - Final Solution")
    print("="*70)
    print()
    print("Challenge: MD5 Collision")
    print("Hint: Fake flag is not useless, developer tools are your friend")
    print()
    print("Solution:")
    print("1. Create two different files with same MD5 hash")
    print("2. Upload the first file to /collision endpoint")
    print("3. Check response headers for X-Secret")
    print("4. Flag format: Kaal{X-Secret}")
    print("="*70)
    print()
    
    solve()
