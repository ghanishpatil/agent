#!/usr/bin/env python3
"""Extract the actual password"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("EXTRACTING PASSWORD")
print("="*80)

# Candidates found so far
candidates = [
    "WpGqRn0",  # Found near "Success"
    "VurrAj0",  # Found near "raj"
    "raj045735",  # Author name
    "RAJ",
    "raj",
]

print("\nPASSWORD CANDIDATES:")
for i, c in enumerate(candidates, 1):
    print(f"{i}. {c}")

# Let's look more carefully at the context around these strings
with zipfile.ZipFile(APK_PATH, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            
            # Check for WpGqRn0
            if b'WpGqRn0' in content:
                print(f"\n[WpGqRn0 found in {name}]")
                pos = content.find(b'WpGqRn0')
                context = content[max(0, pos-150):pos+150]
                print(f"Context: {context}")
                
                # Look for nearby strings
                strings = re.findall(rb'[A-Za-z0-9_]{3,20}', context)
                print("\nNearby strings:")
                for s in strings:
                    try:
                        print(f"  {s.decode('utf-8')}")
                    except:
                        pass
            
            # Check for VurrAj0
            if b'VurrAj0' in content:
                print(f"\n[VurrAj0 found in {name}]")
                pos = content.find(b'VurrAj0')
                context = content[max(0, pos-150):pos+150]
                print(f"Context: {context}")
                
                strings = re.findall(rb'[A-Za-z0-9_]{3,20}', context)
                print("\nNearby strings:")
                for s in strings:
                    try:
                        print(f"  {s.decode('utf-8')}")
                    except:
                        pass

print("\n" + "="*80)
print("\nTRY THESE PASSWORDS IN ORDER:")
print("1. WpGqRn0")
print("2. VurrAj0")
print("3. raj045735")
print("4. RAJ")
print("="*80)
