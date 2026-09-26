#!/usr/bin/env python3
"""
Test uploading the bonus image from the website
Maybe we need to create a collision with THAT image
"""

import requests
import hashlib

URL = "http://138.199.163.92:12871"

def download_bonus_image():
    """Download the bonus image"""
    r = requests.get(f"{URL}/image.png")
    with open("bonus_image.png", "wb") as f:
        f.write(r.content)
    return r.content

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

def test_all_combinations():
    """Test different upload combinations"""
    bonus_img = download_bonus_image()
    file1, file2 = create_collision_files()
    
    print(f"[+] Bonus image MD5: {hashlib.md5(bonus_img).hexdigest()}")
    print(f"[+] Collision file1 MD5: {hashlib.md5(file1).hexdigest()}")
    print(f"[+] Collision file2 MD5: {hashlib.md5(file2).hexdigest()}")
    
    # Test 1: Upload bonus image twice
    print("\n" + "="*70)
    print("Test 1: Upload bonus image twice")
    print("="*70)
    session1 = requests.Session()
    
    files = {'image': ('bonus.png', bonus_img, 'image/png')}
    r1 = session1.post(f"{URL}/collision", files=files)
    print(f"[1] {r1.text}")
    
    files = {'image': ('bonus.png', bonus_img, 'image/png')}
    r2 = session1.post(f"{URL}/collision", files=files)
    print(f"[2] {r2.text}")
    
    if 'Kaal{' in r2.text:
        print(f"[!] FLAG: {r2.text}")
    
    # Test 2: Upload bonus, then collision file1
    print("\n" + "="*70)
    print("Test 2: Upload bonus image, then collision file1")
    print("="*70)
    session2 = requests.Session()
    
    files = {'image': ('bonus.png', bonus_img, 'image/png')}
    r1 = session2.post(f"{URL}/collision", files=files)
    print(f"[1] {r1.text}")
    
    files = {'image': ('coll1.png', file1, 'image/png')}
    r2 = session2.post(f"{URL}/collision", files=files)
    print(f"[2] {r2.text}")
    
    if 'Kaal{' in r2.text:
        print(f"[!] FLAG: {r2.text}")
    
    # Test 3: Upload collision file1, then bonus
    print("\n" + "="*70)
    print("Test 3: Upload collision file1, then bonus image")
    print("="*70)
    session3 = requests.Session()
    
    files = {'image': ('coll1.png', file1, 'image/png')}
    r1 = session3.post(f"{URL}/collision", files=files)
    print(f"[1] {r1.text}")
    print(f"[1] Headers: {dict(r1.headers)}")
    
    files = {'image': ('bonus.png', bonus_img, 'image/png')}
    r2 = session3.post(f"{URL}/collision", files=files)
    print(f"[2] {r2.text}")
    print(f"[2] Headers: {dict(r2.headers)}")
    
    if 'Kaal{' in r2.text:
        print(f"[!] FLAG: {r2.text}")
    
    # Test 4: Create collision with bonus image as prefix
    print("\n" + "="*70)
    print("Test 4: Append collision blocks to bonus image")
    print("="*70)
    
    # Create two files: bonus_image + collision_block1 and bonus_image + collision_block2
    modified1 = bonus_img + file1
    modified2 = bonus_img + file2
    
    print(f"[+] Modified1 MD5: {hashlib.md5(modified1).hexdigest()}")
    print(f"[+] Modified2 MD5: {hashlib.md5(modified2).hexdigest()}")
    print(f"[+] MD5 match: {hashlib.md5(modified1).hexdigest() == hashlib.md5(modified2).hexdigest()}")
    
    session4 = requests.Session()
    
    files = {'image': ('mod1.png', modified1, 'image/png')}
    r1 = session4.post(f"{URL}/collision", files=files)
    print(f"[1] {r1.text}")
    
    files = {'image': ('mod2.png', modified2, 'image/png')}
    r2 = session4.post(f"{URL}/collision", files=files)
    print(f"[2] {r2.text}")
    
    if 'Kaal{' in r2.text:
        print(f"[!] FLAG: {r2.text}")

if __name__ == "__main__":
    print("="*70)
    print("Test with Bonus Image")
    print("="*70)
    test_all_combinations()
