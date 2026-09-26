#!/usr/bin/env python3
"""
Create actual different files with same MD5
Using the fastcoll technique properly
"""

import requests
import hashlib
import subprocess
import os

TARGET_URL = "http://138.199.163.92:12871/"

def try_different_collision_source():
    """Try downloading from a different source"""
    print("="*60)
    print("Trying Different Collision Sources")
    print("="*60)
    
    # Try the famous "shattered" PDF collision
    urls = [
        ("https://shattered.io/static/shattered-1.pdf", "shattered1.pdf"),
        ("https://shattered.io/static/shattered-2.pdf", "shattered2.pdf"),
    ]
    
    for url, filename in urls:
        try:
            print(f"\n[*] Downloading {url}...")
            resp = requests.get(url, timeout=15)
            
            if resp.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                
                hash_val = hashlib.md5(resp.content).hexdigest()
                sha1_val = hashlib.sha1(resp.content).hexdigest()
                print(f"[+] Saved {filename}")
                print(f"[+] MD5: {hash_val}")
                print(f"[+] SHA1: {sha1_val}")
        except Exception as e:
            print(f"[-] Error: {e}")
    
    # Check if they're different but have same hash
    try:
        with open('shattered1.pdf', 'rb') as f1:
            data1 = f1.read()
        with open('shattered2.pdf', 'rb') as f2:
            data2 = f2.read()
        
        print(f"\n[*] Files are different: {data1 != data2}")
        print(f"[*] MD5 match: {hashlib.md5(data1).hexdigest() == hashlib.md5(data2).hexdigest()}")
        print(f"[*] SHA1 match: {hashlib.sha1(data1).hexdigest() == hashlib.sha1(data2).hexdigest()}")
        
        if data1 != data2 and hashlib.md5(data1).hexdigest() == hashlib.md5(data2).hexdigest():
            return 'shattered1.pdf', 'shattered2.pdf'
    except:
        pass
    
    return None, None

def upload_and_test(file1, file2):
    """Upload collision files"""
    if not file1 or not file2:
        return None
    
    print("\n" + "="*60)
    print(f"Testing {file1} and {file2}")
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
                return flag.group(0)
    
    return None

def create_image_collision():
    """
    Create two different images with same MD5
    Using a technique that embeds collision blocks in image metadata
    """
    print("\n" + "="*60)
    print("Creating Image-Based Collision")
    print("="*60)
    
    from PIL import Image
    import io
    
    # Create two different images
    img1 = Image.new('RGB', (10, 10), color='red')
    img2 = Image.new('RGB', (10, 10), color='blue')
    
    # Save to bytes
    buf1 = io.BytesIO()
    buf2 = io.BytesIO()
    
    img1.save(buf1, format='PNG')
    img2.save(buf2, format='PNG')
    
    data1 = buf1.getvalue()
    data2 = buf2.getvalue()
    
    # Insert collision blocks into PNG metadata/comments
    # PNG allows tEXt chunks which we can use
    
    # Collision blocks
    collision1 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70"
    )
    
    collision2 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70"
    )
    
    # Prepend collision blocks to image data
    final1 = collision1 + data1
    final2 = collision2 + data2
    
    with open('img_collision1.png', 'wb') as f:
        f.write(final1)
    
    with open('img_collision2.png', 'wb') as f:
        f.write(final2)
    
    hash1 = hashlib.md5(final1).hexdigest()
    hash2 = hashlib.md5(final2).hexdigest()
    
    print(f"[+] Image 1 MD5: {hash1}")
    print(f"[+] Image 2 MD5: {hash2}")
    print(f"[+] Match: {hash1 == hash2}")
    
    if hash1 == hash2:
        return 'img_collision1.png', 'img_collision2.png'
    
    return None, None

def main():
    print("Real MD5 Collision Creation")
    print()
    
    # Try shattered PDFs
    file1, file2 = try_different_collision_source()
    if file1 and file2:
        flag = upload_and_test(file1, file2)
        if flag:
            print(f"\n[!!!] FLAG: {flag}")
            return
    
    # Try image collision
    file1, file2 = create_image_collision()
    if file1 and file2:
        flag = upload_and_test(file1, file2)
        if flag:
            print(f"\n[!!!] FLAG: {flag}")
            return
    
    print("\n" + "="*60)
    print("Still need proper collision files")
    print("="*60)

if __name__ == "__main__":
    main()
