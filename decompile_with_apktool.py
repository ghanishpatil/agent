#!/usr/bin/env python3
"""Try to find password and flag by analyzing strings more carefully"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("DEEP STRING ANALYSIS")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    # Read all DEX files
    for name in z.namelist():
        if name.endswith('.dex'):
            print(f"\n[Analyzing {name}]")
            content = z.read(name)
            
            # Look for the two partial flags we found
            if b'Kaal{GOOD_PROGRESS}' in content and b'Kaal{IT_My_BE}' in content:
                print("Found both partial flags!")
                
                # Find their positions
                pos1 = content.find(b'Kaal{GOOD_PROGRESS}')
                pos2 = content.find(b'Kaal{IT_My_BE}')
                
                print(f"Position 1: {pos1}")
                print(f"Position 2: {pos2}")
                
                # Check if they're adjacent or if there's something between them
                if pos2 > pos1:
                    between = content[pos1:pos2+len(b'Kaal{IT_My_BE}')]
                    print(f"\nData between flags:")
                    print(between[:200])
                    
                    # Try to find if they should be concatenated
                    # Look for any other Kaal{ patterns nearby
                    nearby = content[max(0, pos1-100):pos2+100]
                    all_kaal = re.findall(rb'Kaal\{[^}]*\}?', nearby)
                    print(f"\nAll Kaal patterns nearby:")
                    for k in all_kaal:
                        print(f"  {k}")
            
            # Search for complete flag patterns (longer than what we found)
            long_flags = re.findall(rb'Kaal\{[A-Za-z0-9_]{20,}\}', content)
            if long_flags:
                print(f"\nLong flags found:")
                for f in long_flags:
                    print(f"  {f.decode('utf-8', errors='ignore')}")
            
            # Look for strings that might be the password
            # The hint says "Password Is Near RAJ But Raj Is Lost In Code"
            print(f"\n[Looking for password near RAJ]")
            
            # Find all RAJ occurrences
            raj_positions = [m.start() for m in re.finditer(rb'RAJ', content)]
            print(f"Found {len(raj_positions)} RAJ occurrences")
            
            # Check context around each RAJ
            for i, pos in enumerate(raj_positions[:10]):  # Check first 10
                context = content[max(0, pos-50):pos+50]
                # Look for readable strings
                readable = re.findall(rb'[A-Za-z0-9_]{5,20}', context)
                if readable:
                    print(f"\nRAJ #{i+1} at {pos}:")
                    print(f"  Context: {readable}")
            
            # Look for method/class names containing RAJ
            raj_identifiers = re.findall(rb'[A-Za-z_][A-Za-z0-9_]*RAJ[A-Za-z0-9_]*', content)
            if raj_identifiers:
                print(f"\nRAJ identifiers:")
                for ident in set(raj_identifiers[:20]):
                    try:
                        print(f"  {ident.decode('utf-8', errors='ignore')}")
                    except:
                        pass
            
            # Look for strings that look like passwords (alphanumeric, 6-20 chars)
            print(f"\n[Potential passwords]")
            # Look near "password" strings
            password_positions = [m.start() for m in re.finditer(rb'password', content, re.IGNORECASE)]
            for pos in password_positions[:5]:
                context = content[pos:pos+100]
                passwords = re.findall(rb'[A-Za-z][A-Za-z0-9]{5,15}', context)
                if passwords:
                    print(f"  Near 'password': {passwords[:5]}")

print("\n" + "="*80)
