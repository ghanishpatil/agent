#!/usr/bin/env python3
"""
Hardcore solve - download real MD5 collisions and extract everything from the grid
"""

import requests
import hashlib
from PIL import Image
import io
import re

TARGET_URL = "http://138.199.163.92:12871/"

def download_known_md5_collisions():
    """Download actual known MD5 collision files from the internet"""
    print("="*60)
    print("Downloading Known MD5 Collision Files")
    print("="*60)
    
    # These are famous MD5 collision files available online
    collision_urls = [
        # Peter Selinger's MD5 collision examples
        ("https://www.mscs.dal.ca/~selinger/md5collision/md5-1.bin", "collision_a.bin"),
        ("https://www.mscs.dal.ca/~selinger/md5collision/md5-2.bin", "collision_b.bin"),
    ]
    
    files_downloaded = []
    
    for url, filename in collision_urls:
        try:
            print(f"\n[*] Downloading {url}...")
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                
                # Calculate hash
                hash_val = hashlib.md5(resp.content).hexdigest()
                print(f"[+] Saved {filename} ({len(resp.content)} bytes)")
                print(f"[+] MD5: {hash_val}")
                
                files_downloaded.append(filename)
            else:
                print(f"[-] Failed: {resp.status_code}")
        except Exception as e:
            print(f"[-] Error: {e}")
    
    return files_downloaded

def upload_collision_files(files):
    """Upload the collision files"""
    if len(files) < 2:
        print("[-] Need at least 2 files")
        return None
    
    print("\n" + "="*60)
    print("Uploading Collision Files")
    print("="*60)
    
    session = requests.Session()
    
    for i, filename in enumerate(files):
        print(f"\n[*] Uploading {filename}...")
        
        try:
            with open(filename, 'rb') as f:
                files_data = {'image': f}
                resp = session.post(TARGET_URL + 'collision', files=files_data)
            
            print(f"[+] Status: {resp.status_code}")
            print(f"[+] Response: {resp.text}")
            
            # Check for flag
            if 'kaal{' in resp.text.lower():
                flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                if flag:
                    print(f"\n[!!!] FLAG FOUND: {flag.group(0)}")
                    return flag.group(0)
        except Exception as e:
            print(f"[-] Error: {e}")
    
    return None

def extract_grid_from_image():
    """Extract and analyze the bonus grid image in detail"""
    print("\n" + "="*60)
    print("Deep Analysis of Bonus Grid")
    print("="*60)
    
    try:
        img = Image.open('kaalchakra_image.png')
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get image data
        pixels = img.load()
        width, height = img.size
        
        print(f"[*] Image size: {width}x{height}")
        
        # Try to extract text regions
        # The grid appears to be in a specific area
        # Let's sample different regions
        
        # Check for patterns in pixel values
        print("\n[*] Analyzing pixel patterns...")
        
        # Look for text-like regions (high contrast areas)
        text_regions = []
        
        for y in range(0, height, 10):
            for x in range(0, width, 10):
                r, g, b = pixels[x, y]
                # Check if it's a text-like color (dark on light or light on dark)
                if (r < 50 and g < 50 and b < 50) or (r > 200 and g > 200 and b > 200):
                    text_regions.append((x, y))
        
        print(f"[*] Found {len(text_regions)} potential text regions")
        
        # Try to extract the grid structure
        # The grid from the screenshot appears to be a table
        # Let's try to identify the table boundaries
        
        # Save a cropped version focusing on the grid area
        # From the screenshot, the grid appears to be in the right half
        if width > 400:
            grid_area = img.crop((width//2, 0, width, height))
            grid_area.save('grid_cropped.png')
            print("[+] Saved cropped grid to grid_cropped.png")
        
        # Try to read any embedded text data
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()
        
        # Check for hidden text in PNG chunks
        print("\n[*] Checking PNG chunks...")
        
        # Look for text chunks (tEXt, zTXt, iTXt)
        i = 8  # Skip PNG signature
        while i < len(img_data):
            if i + 8 > len(img_data):
                break
            
            # Read chunk length
            chunk_len = int.from_bytes(img_data[i:i+4], 'big')
            chunk_type = img_data[i+4:i+8].decode('latin-1', errors='ignore')
            
            if chunk_type in ['tEXt', 'zTXt', 'iTXt']:
                chunk_data = img_data[i+8:i+8+chunk_len]
                print(f"[+] Found {chunk_type} chunk: {chunk_data[:100]}")
                
                if b'kaal{' in chunk_data.lower() or b'flag' in chunk_data.lower():
                    print(f"[!!!] FLAG IN PNG CHUNK!")
                    text = chunk_data.decode('latin-1', errors='ignore')
                    flag = re.search(r'Kaal\{[^}]+\}', text, re.IGNORECASE)
                    if flag:
                        return flag.group(0)
            
            i += 12 + chunk_len  # Move to next chunk
        
    except Exception as e:
        print(f"[-] Error: {e}")
    
    return None

def try_alternative_collision_methods():
    """Try creating collisions using different methods"""
    print("\n" + "="*60)
    print("Alternative Collision Methods")
    print("="*60)
    
    # Method 1: Use identical files but with different names
    print("\n[*] Method 1: Testing server behavior...")
    
    session = requests.Session()
    
    # Create a simple file
    test_data = b"PUPPY" * 100
    
    with open('puppy_test1.bin', 'wb') as f:
        f.write(test_data)
    
    # Upload it twice
    with open('puppy_test1.bin', 'rb') as f:
        resp1 = session.post(TARGET_URL + 'collision', files={'image': f})
    
    print(f"[*] First upload: {resp1.text}")
    
    # Upload again
    with open('puppy_test1.bin', 'rb') as f:
        resp2 = session.post(TARGET_URL + 'collision', files={'image': f})
    
    print(f"[*] Second upload: {resp2.text}")
    
    # Method 2: Try uploading with different content-type
    print("\n[*] Method 2: Different content types...")
    
    with open('puppy_test1.bin', 'rb') as f:
        files = {'image': ('puppy.jpg', f, 'image/jpeg')}
        resp3 = session.post(TARGET_URL + 'collision', files=files)
    
    print(f"[*] JPEG type: {resp3.text}")

def main():
    print("HARDCORE KAALCHAKRA SOLVER")
    print()
    
    # Step 1: Try to extract flag from grid image
    print("[*] Step 1: Analyzing bonus grid...")
    flag = extract_grid_from_image()
    if flag:
        print(f"\n{'='*60}")
        print(f"FLAG FOUND: {flag}")
        print(f"{'='*60}")
        return
    
    # Step 2: Download known MD5 collisions
    print("\n[*] Step 2: Downloading known MD5 collisions...")
    files = download_known_md5_collisions()
    
    if files:
        # Step 3: Upload collision files
        print("\n[*] Step 3: Uploading collision files...")
        flag = upload_collision_files(files)
        
        if flag:
            print(f"\n{'='*60}")
            print(f"FLAG FOUND: {flag}")
            print(f"{'='*60}")
            return
    
    # Step 4: Try alternative methods
    print("\n[*] Step 4: Trying alternative methods...")
    try_alternative_collision_methods()
    
    print("\n" + "="*60)
    print("All methods attempted")
    print("="*60)

if __name__ == "__main__":
    main()
