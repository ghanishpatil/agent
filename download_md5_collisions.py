#!/usr/bin/env python3
"""
Download known MD5 collision files and test them
"""

import requests
import hashlib
import io

TARGET_URL = "http://138.199.163.92:12871/"

def download_known_collisions():
    """Download famous MD5 collision files from the internet"""
    print("="*60)
    print("Downloading Known MD5 Collision Files")
    print("="*60)
    
    # Try to download the famous "hello" collision files
    # These are publicly available MD5 collision examples
    
    collision_urls = [
        # Marc Stevens' collision examples
        ("https://marc-stevens.nl/research/md5-1block-collision/md5-1block-collision-1.bin", "collision_a.bin"),
        ("https://marc-stevens.nl/research/md5-1block-collision/md5-1block-collision-2.bin", "collision_b.bin"),
    ]
    
    files_downloaded = []
    
    for url, filename in collision_urls:
        try:
            print(f"\n[*] Downloading {url}...")
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                
                hash_val = hashlib.md5(resp.content).hexdigest()
                print(f"[+] Saved {filename} ({len(resp.content)} bytes)")
                print(f"[+] MD5: {hash_val}")
                files_downloaded.append(filename)
            else:
                print(f"[-] Failed: {resp.status_code}")
        except Exception as e:
            print(f"[-] Error: {e}")
    
    return files_downloaded

def create_collision_with_prefix():
    """
    Create collision files with a common prefix
    This is the technique used in real MD5 collisions
    """
    print("\n" + "="*60)
    print("Creating Collision with Prefix")
    print("="*60)
    
    # Use the collision blocks that are known to work
    # These specific blocks create a collision when used correctly
    
    # Common prefix
    prefix = b""
    
    # First collision block (128 bytes)
    block1 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70"
    )
    
    # Second collision block (128 bytes) - differs in specific bytes
    block2 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70"
    )
    
    # Suffix (can be anything)
    suffix = b"\x00" * 64  # Padding to make it 192 bytes total
    
    file1 = prefix + block1 + suffix
    file2 = prefix + block2 + suffix
    
    with open('manual_collision1.bin', 'wb') as f:
        f.write(file1)
    
    with open('manual_collision2.bin', 'wb') as f:
        f.write(file2)
    
    hash1 = hashlib.md5(file1).hexdigest()
    hash2 = hashlib.md5(file2).hexdigest()
    
    print(f"[+] File 1 MD5: {hash1}")
    print(f"[+] File 2 MD5: {hash2}")
    print(f"[+] Match: {hash1 == hash2}")
    
    if hash1 == hash2:
        return 'manual_collision1.bin', 'manual_collision2.bin'
    
    return None, None

def test_all_collision_files():
    """Test all available collision files"""
    print("\n" + "="*60)
    print("Testing All Collision Files")
    print("="*60)
    
    session = requests.Session()
    
    # List of files to try
    files_to_try = [
        ('collision_a.bin', 'collision_b.bin'),
        ('manual_collision1.bin', 'manual_collision2.bin'),
    ]
    
    for file1, file2 in files_to_try:
        try:
            print(f"\n[*] Testing {file1} and {file2}...")
            
            # Check if files exist
            try:
                with open(file1, 'rb') as f:
                    data1 = f.read()
                with open(file2, 'rb') as f:
                    data2 = f.read()
            except FileNotFoundError:
                print(f"[-] Files not found, skipping")
                continue
            
            # Verify they have same hash
            hash1 = hashlib.md5(data1).hexdigest()
            hash2 = hashlib.md5(data2).hexdigest()
            
            print(f"[+] File 1 MD5: {hash1}")
            print(f"[+] File 2 MD5: {hash2}")
            
            if hash1 != hash2:
                print(f"[-] Hashes don't match, skipping")
                continue
            
            print(f"[+] Hashes match! Uploading...")
            
            # Upload first file
            with open(file1, 'rb') as f:
                files = {'image': f}
                resp1 = session.post(TARGET_URL + 'collision', files=files)
            
            print(f"[+] Response 1: {resp1.text}")
            
            # Upload second file
            with open(file2, 'rb') as f:
                files = {'image': f}
                resp2 = session.post(TARGET_URL + 'collision', files=files)
            
            print(f"[+] Response 2: {resp2.text}")
            
            # Check for flag
            for resp in [resp1, resp2]:
                if 'kaal{' in resp.text.lower():
                    import re
                    flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                    if flag:
                        print(f"\n[!!!] FLAG FOUND: {flag.group(0)}")
                        return flag.group(0)
        
        except Exception as e:
            print(f"[-] Error: {e}")
    
    return None

def main():
    print("MD5 Collision Download and Test")
    print()
    
    # Download known collisions
    downloaded = download_known_collisions()
    
    # Create manual collisions
    file1, file2 = create_collision_with_prefix()
    
    # Test all
    flag = test_all_collision_files()
    
    if flag:
        print("\n" + "="*60)
        print(f"SUCCESS! FLAG: {flag}")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("No flag yet - need actual working MD5 collision files")
        print("="*60)

if __name__ == "__main__":
    main()
