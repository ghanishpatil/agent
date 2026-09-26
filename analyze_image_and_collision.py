#!/usr/bin/env python3
"""
Analyze the bonus image and collision behavior more carefully
"""

import requests
import hashlib
from PIL import Image
import io

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

def test_collision_sequence():
    """Test different collision upload sequences"""
    file1, file2 = create_collision_files()
    
    print("[*] Testing collision upload sequences...")
    print(f"[+] File1 MD5: {hashlib.md5(file1).hexdigest()}")
    print(f"[+] File2 MD5: {hashlib.md5(file2).hexdigest()}")
    
    # Test: Upload file1, then file2 (should trigger collision detection)
    print("\n" + "="*70)
    print("Test: Upload file1, then file2 (collision)")
    print("="*70)
    
    session = requests.Session()
    
    # First upload
    files1 = {'image': ('puppy1.png', file1, 'image/png')}
    r1 = session.post(f"{URL}/collision", files=files1)
    print(f"[1] Response: {r1.text}")
    print(f"[1] Headers: X-Prefix={r1.headers.get('X-Prefix')}, X-Secret={r1.headers.get('X-Secret')}")
    
    # Second upload (should detect collision)
    files2 = {'image': ('puppy2.png', file2, 'image/png')}
    r2 = session.post(f"{URL}/collision", files=files2)
    print(f"[2] Response: {r2.text}")
    print(f"[2] Headers: X-Prefix={r2.headers.get('X-Prefix')}, X-Secret={r2.headers.get('X-Secret')}")
    
    # Check if there's a flag in the response
    if 'Kaal{' in r2.text:
        print(f"\n[!] FLAG FOUND: {r2.text}")
        return
    
    # Try accessing different endpoints after collision
    print("\n[*] Trying endpoints after collision detection...")
    
    endpoints = ['/', '/flag', '/secret', '/collision', '/verify', '/check', '/success']
    for endpoint in endpoints:
        r = session.get(f"{URL}{endpoint}")
        if r.status_code == 200 and 'Kaal{' in r.text:
            print(f"[!] FLAG at {endpoint}: {r.text}")
            return
        elif r.status_code == 200 and endpoint not in ['/', '/collision']:
            print(f"[+] {endpoint}: {r.status_code} - {r.text[:100]}")

def analyze_bonus_image():
    """Analyze the bonus puppy image for hidden data"""
    print("\n" + "="*70)
    print("Analyzing bonus image")
    print("="*70)
    
    r = requests.get(f"{URL}/image.png")
    img_data = r.content
    
    print(f"[+] Image size: {len(img_data)} bytes")
    print(f"[+] MD5: {hashlib.md5(img_data).hexdigest()}")
    
    # Check for data after PNG IEND
    iend_marker = b'IEND\xae\x42\x60\x82'
    if iend_marker in img_data:
        iend_pos = img_data.find(iend_marker) + len(iend_marker)
        if iend_pos < len(img_data):
            extra = img_data[iend_pos:]
            print(f"[+] Extra data after IEND: {len(extra)} bytes")
            print(f"    Hex: {extra[:100].hex()}")
            print(f"    Text: {extra[:100]}")
            
            # Try to decode as text
            try:
                text = extra.decode('utf-8', errors='ignore')
                if text.strip():
                    print(f"[+] Decoded text: {text}")
                    if 'Kaal{' in text:
                        print(f"[!] FLAG FOUND: {text}")
            except:
                pass
    
    # Check PNG chunks
    print("\n[*] Checking PNG chunks...")
    pos = 8  # Skip PNG signature
    while pos < len(img_data) - 12:
        try:
            length = int.from_bytes(img_data[pos:pos+4], 'big')
            chunk_type = img_data[pos+4:pos+8].decode('ascii', errors='ignore')
            chunk_data = img_data[pos+8:pos+8+length]
            
            print(f"[+] Chunk: {chunk_type}, Length: {length}")
            
            # Check for text chunks
            if chunk_type in ['tEXt', 'zTXt', 'iTXt']:
                print(f"    Data: {chunk_data[:100]}")
                try:
                    text = chunk_data.decode('utf-8', errors='ignore')
                    if 'Kaal{' in text:
                        print(f"[!] FLAG in {chunk_type}: {text}")
                except:
                    pass
            
            pos += 12 + length
        except:
            break

if __name__ == "__main__":
    print("="*70)
    print("Analyze Image and Collision Behavior")
    print("="*70)
    
    test_collision_sequence()
    analyze_bonus_image()
