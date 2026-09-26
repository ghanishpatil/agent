#!/usr/bin/env python3
"""
Download rockyou.txt and crack the hash
"""

import hashlib
import requests
import gzip
import os

target_hash = "707b10ba2d8020957997e4127c99147091087a71"

print("="*70)
print("DOWNLOADING ROCKYOU.TXT AND CRACKING HASH")
print("="*70)

# Check if rockyou.txt already exists
if os.path.exists('rockyou.txt'):
    print("\nrockyou.txt already exists!")
else:
    print("\nDownloading rockyou.txt...")
    try:
        # Download from GitHub
        url = "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
        
        print(f"Downloading from: {url}")
        response = requests.get(url, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open('rockyou.txt', 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("✓ Downloaded rockyou.txt")
        else:
            print(f"✗ Failed to download: {response.status_code}")
            print("\nTrying alternative source...")
            
            # Try alternative
            url2 = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Leaked-Databases/rockyou.txt.tar.gz"
            print(f"Downloading from: {url2}")
            response = requests.get(url2, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open('rockyou.txt.tar.gz', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("✓ Downloaded rockyou.txt.tar.gz")
                
                # Extract
                import tarfile
                with tarfile.open('rockyou.txt.tar.gz', 'r:gz') as tar:
                    tar.extractall()
                print("✓ Extracted rockyou.txt")
            else:
                print(f"✗ Failed: {response.status_code}")
                
    except Exception as e:
        print(f"✗ Error downloading: {e}")

# Crack the hash
if os.path.exists('rockyou.txt'):
    print("\n" + "="*70)
    print("CRACKING HASH WITH ROCKYOU.TXT")
    print("="*70)
    print(f"\nTarget: {target_hash}")
    print("This may take a few minutes...\n")
    
    try:
        with open('rockyou.txt', 'r', encoding='latin-1', errors='ignore') as f:
            for i, line in enumerate(f):
                pwd = line.strip()
                
                if pwd:  # Skip empty lines
                    h = hashlib.sha1(pwd.encode('latin-1', errors='ignore')).hexdigest()
                    
                    if h == target_hash:
                        print("\n" + "="*70)
                        print("*** PASSWORD FOUND ***")
                        print("="*70)
                        print(f"\nPassword: {pwd}")
                        print(f"Hash: {h}")
                        print(f"Found after trying {i+1} passwords")
                        
                        # Save to file
                        with open('BETRAYAL_PASSWORD.txt', 'w') as out:
                            out.write(f"Password: {pwd}\n")
                            out.write(f"Hash: {h}\n")
                        
                        print("\n✓ Saved to BETRAYAL_PASSWORD.txt")
                        exit(0)
                
                # Progress indicator
                if i % 100000 == 0:
                    print(f"Tried {i:,} passwords...", end='\r')
        
        print(f"\n\n✗ Password not found in rockyou.txt ({i+1:,} passwords tried)")
        
    except Exception as e:
        print(f"\n✗ Error reading rockyou.txt: {e}")
else:
    print("\n✗ rockyou.txt not found. Cannot crack hash.")
    print("\nManual steps:")
    print("1. Download: https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt")
    print("2. Place in current directory")
    print("3. Run this script again")
