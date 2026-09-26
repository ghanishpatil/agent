#!/usr/bin/env python3
"""
Simple APK extraction and analysis
"""
import zipfile
import os
import re

APK_PATH = "D:\\mission-git-hackss\\KaalRaj.apk"

print("="*80)
print("EXTRACTING AND ANALYZING APK")
print("="*80)

# Extract APK
extract_dir = "D:\\mission-git-hackss\\KaalRaj_extracted"

if not os.path.exists(extract_dir):
    os.makedirs(extract_dir)

print(f"\n[Extracting APK]")
try:
    with zipfile.ZipFile(APK_PATH, 'r') as zip_ref:
        # List all files first
        file_list = zip_ref.namelist()
        print(f"Total files in APK: {len(file_list)}")
        
        # Extract only specific files to avoid recursion
        for file in file_list[:100]:  # Limit to first 100 files
            try:
                zip_ref.extract(file, extract_dir)
            except:
                pass
        
        print(f"✓ Extracted files to: {extract_dir}")
        
        # Look for interesting files
        print(f"\n[Interesting files in APK]")
        for file in file_list:
            if any(x in file.lower() for x in ['flag', 'secret', 'key', 'raj', 'password', '.dex', 'manifest']):
                print(f"  {file}")
        
        # Search for "raj" or "RAJ" in file contents
        print(f"\n[Searching for 'raj' in files]")
        for file in file_list:
            if file.endswith(('.xml', '.txt', '.json', '.properties')):
                try:
                    content = zip_ref.read(file).decode('utf-8', errors='ignore')
                    if 'raj' in content.lower() or 'password' in content.lower():
                        print(f"\n  ✓ Found in: {file}")
                        # Show relevant lines
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'raj' in line.lower() or 'password' in line.lower():
                                print(f"    Line {i}: {line[:100]}")
                except:
                    pass
        
        # Check DEX files for strings
        print(f"\n[Checking DEX files for strings]")
        for file in file_list:
            if file.endswith('.dex'):
                print(f"\n  Checking: {file}")
                try:
                    content = zip_ref.read(file)
                    # Look for printable strings
                    strings = re.findall(b'[\x20-\x7e]{6,}', content)
                    for s in strings:
                        try:
                            text = s.decode('utf-8')
                            if 'raj' in text.lower() or 'password' in text.lower() or 'Kaal{' in text:
                                print(f"    {text}")
                        except:
                            pass
                except Exception as e:
                    print(f"    Error: {e}")
                    
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*80)
