#!/usr/bin/env python3
"""
Deep analysis of Time Traveler challenge
The X-Secret might be a key or hint to something else
"""

import requests
import hashlib
import base64

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

def get_headers():
    """Get the secret headers"""
    file1, file2 = create_collision_files()
    
    files = {'image': ('puppy1.png', file1, 'image/png')}
    r = requests.post(f"{URL}/collision", files=files)
    
    prefix = r.headers.get('X-Prefix', '')
    secret = r.headers.get('X-Secret', '')
    
    return prefix, secret

def explore_with_secret(prefix, secret):
    """Try different things with the secret"""
    print(f"[*] Prefix: {prefix}")
    print(f"[*] Secret: {secret}")
    
    # Try using secret as a path parameter
    print("\n[1] Try /{prefix} with secret parameter")
    r = requests.get(f"{URL}/{prefix}", params={'secret': secret})
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        print(f"    Response: {r.text[:500]}")
        if 'Kaal{' in r.text:
            print(f"    [!] FLAG FOUND: {r.text}")
    
    # Try /kaal (reversed prefix)
    print("\n[2] Try /kaal with secret")
    r = requests.get(f"{URL}/kaal", params={'secret': secret})
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        print(f"    Response: {r.text[:500]}")
        if 'Kaal{' in r.text:
            print(f"    [!] FLAG FOUND: {r.text}")
    
    # Try POST to collision with secret
    print("\n[3] POST /collision with secret parameter")
    r = requests.post(f"{URL}/collision", data={'secret': secret})
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.text[:500]}")
    if 'Kaal{' in r.text:
        print(f"    [!] FLAG FOUND: {r.text}")
    
    # Try GET /collision with secret
    print("\n[4] GET /collision with secret parameter")
    r = requests.get(f"{URL}/collision", params={'secret': secret})
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        print(f"    Response: {r.text[:500]}")
        if 'Kaal{' in r.text:
            print(f"    [!] FLAG FOUND: {r.text}")
    
    # Check if we need to upload BOTH collision files
    print("\n[5] Upload both collision files in same session")
    session = requests.Session()
    file1, file2 = create_collision_files()
    
    files1 = {'image': ('puppy1.png', file1, 'image/png')}
    r1 = session.post(f"{URL}/collision", files=files1)
    print(f"    First upload: {r1.text}")
    
    files2 = {'image': ('puppy2.png', file2, 'image/png')}
    r2 = session.post(f"{URL}/collision", files=files2)
    print(f"    Second upload: {r2.text}")
    
    if 'Kaal{' in r2.text:
        print(f"    [!] FLAG FOUND: {r2.text}")
    
    # Check all response headers
    print(f"\n    All headers from second upload:")
    for k, v in r2.headers.items():
        print(f"      {k}: {v}")
    
    # Try accessing with cookies
    print("\n[6] Try accessing root with session cookies")
    r = session.get(f"{URL}/")
    if 'Kaal{' in r.text:
        print(f"    [!] FLAG in root page: {r.text}")
    
    # Check for flag endpoint with session
    print("\n[7] Try /flag with session")
    r = session.get(f"{URL}/flag")
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        print(f"    Response: {r.text[:500]}")
        if 'Kaal{' in r.text:
            print(f"    [!] FLAG FOUND: {r.text}")
    
    # Try /verify or /check
    print("\n[8] Try /verify endpoint")
    r = session.get(f"{URL}/verify")
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        print(f"    Response: {r.text[:500]}")
        if 'Kaal{' in r.text:
            print(f"    [!] FLAG FOUND: {r.text}")
    
    # Check image.png with session
    print("\n[9] Check /image.png with session")
    r = session.get(f"{URL}/image.png")
    print(f"    Status: {r.status_code}")
    print(f"    Content-Type: {r.headers.get('Content-Type')}")
    print(f"    Size: {len(r.content)} bytes")
    
    # Check for flag in image.png response headers
    for k, v in r.headers.items():
        if 'flag' in k.lower() or 'kaal' in str(v).lower():
            print(f"    [!] Interesting header: {k}: {v}")

if __name__ == "__main__":
    print("="*70)
    print("Deep Time Traveler Analysis")
    print("="*70)
    
    prefix, secret = get_headers()
    explore_with_secret(prefix, secret)
