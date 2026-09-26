#!/usr/bin/env python3
"""Extract both embedded files properly"""
import zipfile
import os

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"
OUTPUT_DIR = "apk_extracted"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*80)
print("EXTRACTING EMBEDDED FILES")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    embedded_files = [name for name in z.namelist() if name.startswith('assets/') and len(name) > 100]
    
    print(f"\nFound {len(embedded_files)} embedded files with long names")
    
    for i, name in enumerate(embedded_files):
        data = z.read(name)
        print(f"\n[File #{i+1}]")
        print(f"  Name length: {len(name)}")
        print(f"  Data size: {len(data)} bytes ({len(data)/1024/1024:.2f} MB)")
        print(f"  First 50 bytes: {data[:50]}")
        
        # Save with index
        output_path = os.path.join(OUTPUT_DIR, f"embedded_{i+1}.bin")
        with open(output_path, 'wb') as f:
            f.write(data)
        print(f"  Saved to: {output_path}")
        
        # Check if it contains the key
        if b'401745546b5c0affd89343914f88bab4c82' in data:
            print(f"  ✓ Contains the key!")
            
            # Extract the key
            key_pos = data.find(b'401745546b5c0affd89343914f88bab4c82')
            print(f"  Key at position: {key_pos}")
            print(f"  Context: {data[max(0, key_pos-20):key_pos+60]}")

print("\n" + "="*80)
