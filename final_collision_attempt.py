#!/usr/bin/env python3
"""
Final attempt - maybe I need to actually get "Collision detected!" message
Let me check what responses are possible
"""

import requests
import hashlib

URL = "http://138.199.163.92:12871"

def test_all_scenarios():
    """Test all possible upload scenarios"""
    
    # Get the bonus image
    r = requests.get(f"{URL}/image.png")
    bonus_img = r.content
    
    # Get collision blocks
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
    
    print(f"[+] Bonus MD5: {hashlib.md5(bonus_img).hexdigest()}")
    print(f"[+] Coll1 MD5: {hashlib.md5(file1).hexdigest()}")
    print(f"[+] Coll2 MD5: {hashlib.md5(file2).hexdigest()}")
    print(f"[+] Coll1 == Coll2: {hashlib.md5(file1).hexdigest() == hashlib.md5(file2).hexdigest()}")
    print(f"[+] Coll1 != Coll2 (bytes): {file1 != file2}")
    
    # Observed responses:
    # - "First puppy added 🐶" - first upload
    # - "Looks like the same puppy 😏" - same file uploaded twice (same MD5, same bytes)
    # - "Still not matching 😏" - different files (different MD5 or different bytes with same MD5)
    
    # What we need: Two DIFFERENT files with SAME MD5
    # The collision blocks satisfy this!
    
    # Let me check the server logic more carefully
    print("\n" + "="*70)
    print("Testing: Upload coll1, then coll2 (TRUE MD5 collision)")
    print("="*70)
    
    session = requests.Session()
    
    # Upload file1
    files = {'image': ('img1.png', file1, 'image/png')}
    r1 = session.post(f"{URL}/collision", files=files)
    print(f"\n[Upload 1]")
    print(f"  Response: {r1.text}")
    print(f"  X-Prefix: {r1.headers.get('X-Prefix')}")
    print(f"  X-Secret: {r1.headers.get('X-Secret')}")
    
    # Upload file2 (different bytes, same MD5)
    files = {'image': ('img2.png', file2, 'image/png')}
    r2 = session.post(f"{URL}/collision", files=files)
    print(f"\n[Upload 2]")
    print(f"  Response: {r2.text}")
    print(f"  X-Prefix: {r2.headers.get('X-Prefix')}")
    print(f"  X-Secret: {r2.headers.get('X-Secret')}")
    
    # Check all possible places for flag
    print(f"\n[*] Checking for flag...")
    
    if 'Kaal{' in r2.text:
        print(f"  [!] FLAG in response: {r2.text}")
    
    for k, v in r2.headers.items():
        if 'kaal{' in str(v).lower():
            print(f"  [!] FLAG in header {k}: {v}")
    
    # Try GET requests after collision
    for endpoint in ['/', '/flag', '/success', '/win', '/collision']:
        r = session.get(f"{URL}{endpoint}")
        if 'Kaal{' in r.text:
            print(f"  [!] FLAG at {endpoint}: {r.text}")

if __name__ == "__main__":
    print("="*70)
    print("Final Collision Attempt")
    print("="*70)
    test_all_scenarios()
