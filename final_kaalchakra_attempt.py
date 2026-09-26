#!/usr/bin/env python3
"""
Final attempt - try different approaches
"""

import requests
import hashlib

TARGET_URL = "http://138.199.163.92:12871/"

def check_if_grid_has_flag():
    """Check if the bonus grid image itself contains the flag"""
    print("="*60)
    print("Checking Bonus Grid Image")
    print("="*60)
    
    session = requests.Session()
    
    # Download the image
    resp = session.get(TARGET_URL + 'image.png')
    
    # Check if flag is in the image bytes
    if b'kaal{' in resp.content.lower() or b'Kaal{' in resp.content:
        print("[!!!] FLAG FOUND IN IMAGE BYTES!")
        # Extract it
        import re
        text = resp.content.decode('latin-1', errors='ignore')
        flag = re.search(r'Kaal\{[^}]+\}', text, re.IGNORECASE)
        if flag:
            print(f"FLAG: {flag.group(0)}")
            return flag.group(0)
    
    # Try strings command equivalent
    printable = ''.join(chr(b) if 32 <= b < 127 else '' for b in resp.content)
    if 'kaal{' in printable.lower():
        print("[!!!] FLAG FOUND IN PRINTABLE STRINGS!")
        import re
        flag = re.search(r'Kaal\{[^}]+\}', printable, re.IGNORECASE)
        if flag:
            print(f"FLAG: {flag.group(0)}")
            return flag.group(0)
    
    print("[-] No flag found in image")
    return None

def try_uploading_known_formats():
    """Try uploading files in different formats"""
    print("\n" + "="*60)
    print("Trying Different File Formats")
    print("="*60)
    
    session = requests.Session()
    
    # Create a simple text file claiming to be an image
    test_data = b"GIF89a" + b"A" * 100  # GIF header + data
    
    with open('test.gif', 'wb') as f:
        f.write(test_data)
    
    with open('test.gif', 'rb') as f:
        files = {'image': f}
        resp = session.post(TARGET_URL + 'collision', files=files)
    
    print(f"[*] GIF upload: {resp.text}")
    
    # Try uploading the same data twice with same hash
    hash1 = hashlib.md5(test_data).hexdigest()
    print(f"[*] Test data MD5: {hash1}")

def check_other_endpoints():
    """Check for other endpoints that might give hints"""
    print("\n" + "="*60)
    print("Checking Other Endpoints")
    print("="*60)
    
    session = requests.Session()
    
    endpoints = [
        '/flag',
        '/hint',
        '/solution',
        '/collision',
        '/api/flag',
        '/api/collision',
        '/download',
        '/files',
    ]
    
    for endpoint in endpoints:
        try:
            resp = session.get(TARGET_URL.rstrip('/') + endpoint)
            if resp.status_code != 404:
                print(f"\n[+] {endpoint}: {resp.status_code}")
                if len(resp.text) < 200:
                    print(f"    {resp.text}")
                
                if 'kaal{' in resp.text.lower():
                    import re
                    flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                    if flag:
                        print(f"\n[!!!] FLAG: {flag.group(0)}")
                        return flag.group(0)
        except:
            pass

def main():
    print("Final Kaalchakra Attempt")
    print()
    
    # Check if flag is in the grid image
    result = check_if_grid_has_flag()
    if result:
        return
    
    # Check other endpoints
    result = check_other_endpoints()
    if result:
        return
    
    # Try different formats
    try_uploading_known_formats()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("To solve this challenge, you need:")
    print("1. Two different files with the same MD5 hash")
    print("2. Use tools like 'fastcoll' or download known MD5 collisions")
    print("3. The bonus grid likely contains a cipher to decode")
    print("4. Upload both collision files to get the flag")

if __name__ == "__main__":
    main()
