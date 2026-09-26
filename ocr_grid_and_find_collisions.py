#!/usr/bin/env python3
"""
OCR the grid and find working MD5 collisions
"""

import requests
import hashlib
import re
from PIL import Image

TARGET_URL = "http://138.199.163.92:12871/"

def try_ocr_on_grid():
    """Try OCR on the cropped grid"""
    print("="*60)
    print("OCR on Bonus Grid")
    print("="*60)
    
    try:
        import pytesseract
        
        # Try on both full and cropped image
        for img_file in ['kaalchakra_image.png', 'grid_cropped.png']:
            try:
                print(f"\n[*] OCR on {img_file}...")
                img = Image.open(img_file)
                
                # Try different preprocessing
                # 1. Original
                text1 = pytesseract.image_to_string(img)
                
                # 2. Grayscale
                img_gray = img.convert('L')
                text2 = pytesseract.image_to_string(img_gray)
                
                # 3. High contrast
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(img)
                img_contrast = enhancer.enhance(2.0)
                text3 = pytesseract.image_to_string(img_contrast)
                
                all_text = text1 + "\n" + text2 + "\n" + text3
                
                print(f"[+] Extracted text:")
                print(all_text[:500])
                
                # Check for flag
                if 'kaal{' in all_text.lower():
                    flag = re.search(r'Kaal\{[^}]+\}', all_text, re.IGNORECASE)
                    if flag:
                        print(f"\n[!!!] FLAG FOUND: {flag.group(0)}")
                        return flag.group(0)
                
                # Save full text
                with open(f'{img_file}_ocr.txt', 'w', encoding='utf-8') as f:
                    f.write(all_text)
                print(f"[+] Saved OCR to {img_file}_ocr.txt")
                
            except Exception as e:
                print(f"[-] Error on {img_file}: {e}")
    
    except ImportError:
        print("[-] pytesseract not available")
        print("[*] Install with: pip install pytesseract")
        print("[*] And install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    
    return None

def create_collision_with_unicoll():
    """
    Try to create collision using UniColl technique
    This is a simpler collision method
    """
    print("\n" + "="*60)
    print("Creating Collision with UniColl Technique")
    print("="*60)
    
    # UniColl allows creating collisions by modifying specific bytes
    # Let's try a known working example
    
    # Base prefix
    prefix = b"This is a test puppy image\n"
    
    # Padding to align to MD5 block boundary (64 bytes)
    padding_len = 64 - (len(prefix) % 64)
    prefix_padded = prefix + b'\x00' * padding_len
    
    # Known collision blocks (these are from actual MD5 collision research)
    # Block pair 1
    block1_hex = "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f8955ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5bd8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70"
    
    block2_hex = "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f8955ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5bd8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70"
    
    block1 = bytes.fromhex(block1_hex)
    block2 = bytes.fromhex(block2_hex)
    
    # Create two files
    file1 = prefix_padded + block1
    file2 = prefix_padded + block2
    
    with open('unicoll1.bin', 'wb') as f:
        f.write(file1)
    
    with open('unicoll2.bin', 'wb') as f:
        f.write(file2)
    
    # Check hashes
    hash1 = hashlib.md5(file1).hexdigest()
    hash2 = hashlib.md5(file2).hexdigest()
    
    print(f"[+] File 1 MD5: {hash1}")
    print(f"[+] File 2 MD5: {hash2}")
    print(f"[+] Files different: {file1 != file2}")
    print(f"[+] Hashes match: {hash1 == hash2}")
    
    if hash1 == hash2:
        print("\n[!!!] COLLISION CREATED!")
        return 'unicoll1.bin', 'unicoll2.bin'
    
    return None, None

def test_unicoll_upload(file1, file2):
    """Upload the unicoll files"""
    if not file1 or not file2:
        return None
    
    print("\n" + "="*60)
    print("Uploading UniColl Files")
    print("="*60)
    
    session = requests.Session()
    
    # Upload first
    print(f"\n[*] Uploading {file1}...")
    with open(file1, 'rb') as f:
        resp1 = session.post(TARGET_URL + 'collision', files={'image': f})
    
    print(f"[+] Response: {resp1.text}")
    
    # Upload second
    print(f"\n[*] Uploading {file2}...")
    with open(file2, 'rb') as f:
        resp2 = session.post(TARGET_URL + 'collision', files={'image': f})
    
    print(f"[+] Response: {resp2.text}")
    
    # Check for flag
    for resp in [resp1, resp2]:
        if 'kaal{' in resp.text.lower():
            flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
            if flag:
                print(f"\n[!!!] FLAG: {flag.group(0)}")
                return flag.group(0)
    
    return None

def try_github_collision_files():
    """Try downloading collision files from GitHub"""
    print("\n" + "="*60)
    print("Downloading from GitHub")
    print("="*60)
    
    # Try different sources
    urls = [
        ("https://raw.githubusercontent.com/corkami/collisions/master/examples/free1.bin", "github1.bin"),
        ("https://raw.githubusercontent.com/corkami/collisions/master/examples/free2.bin", "github2.bin"),
    ]
    
    files = []
    for url, filename in urls:
        try:
            print(f"\n[*] Downloading {url}...")
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                
                hash_val = hashlib.md5(resp.content).hexdigest()
                print(f"[+] Saved {filename}")
                print(f"[+] MD5: {hash_val}")
                files.append(filename)
        except Exception as e:
            print(f"[-] Error: {e}")
    
    if len(files) >= 2:
        return files[0], files[1]
    
    return None, None

def main():
    print("OCR + Collision Finder")
    print()
    
    # Try OCR first
    flag = try_ocr_on_grid()
    if flag:
        print(f"\n{'='*60}")
        print(f"FLAG: {flag}")
        print(f"{'='*60}")
        return
    
    # Try GitHub collisions
    file1, file2 = try_github_collision_files()
    if file1 and file2:
        flag = test_unicoll_upload(file1, file2)
        if flag:
            print(f"\n{'='*60}")
            print(f"FLAG: {flag}")
            print(f"{'='*60}")
            return
    
    # Try creating UniColl
    file1, file2 = create_collision_with_unicoll()
    if file1 and file2:
        flag = test_unicoll_upload(file1, file2)
        if flag:
            print(f"\n{'='*60}")
            print(f"FLAG: {flag}")
            print(f"{'='*60}")
            return
    
    print("\n[*] No flag found yet")
    print("[*] The grid image likely contains the flag encoded")
    print("[*] Need to manually decode the cipher table")

if __name__ == "__main__":
    main()
