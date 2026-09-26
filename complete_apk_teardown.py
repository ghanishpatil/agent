#!/usr/bin/env python3
"""Complete APK teardown - extract everything"""
import zipfile
import re
import os

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"
OUTPUT_DIR = "apk_extracted"

print("="*80)
print("COMPLETE APK TEARDOWN")
print("="*80)

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    print(f"\nTotal files in APK: {len(z.namelist())}")
    
    # Extract the embedded APK (the one with long Arabic name)
    print("\n[1] EXTRACTING EMBEDDED APK")
    for name in z.namelist():
        if name.startswith('assets/') and len(name) > 100:
            print(f"  Found: {name[:50]}... (length: {len(name)})")
            data = z.read(name)
            print(f"  Size: {len(data)} bytes")
            
            # Save it
            output_path = os.path.join(OUTPUT_DIR, "embedded_file.bin")
            with open(output_path, 'wb') as f:
                f.write(data)
            print(f"  Saved to: {output_path}")
            
            # Check if it's encrypted/encoded
            print(f"  First 100 bytes: {data[:100]}")
            
            # Try to find any readable strings in it
            strings = re.findall(rb'[\x20-\x7e]{10,}', data)
            if strings:
                print(f"  Found {len(strings)} readable strings")
                print(f"  First 10 strings:")
                for s in strings[:10]:
                    print(f"    {s.decode('utf-8', errors='ignore')}")
    
    # Extract all DEX files
    print("\n[2] EXTRACTING ALL DEX FILES")
    for name in z.namelist():
        if name.endswith('.dex'):
            print(f"  Extracting: {name}")
            data = z.read(name)
            output_path = os.path.join(OUTPUT_DIR, name.replace('/', '_'))
            with open(output_path, 'wb') as f:
                f.write(data)
    
    # Extract all strings from all DEX files
    print("\n[3] EXTRACTING ALL STRINGS FROM DEX FILES")
    all_strings = set()
    
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            strings = re.findall(rb'[\x20-\x7e]{4,50}\x00', content)
            for s in strings:
                try:
                    decoded = s[:-1].decode('utf-8')
                    all_strings.add(decoded)
                except:
                    pass
    
    print(f"  Total unique strings: {len(all_strings)}")
    
    # Save all strings
    strings_file = os.path.join(OUTPUT_DIR, "all_strings.txt")
    with open(strings_file, 'w', encoding='utf-8') as f:
        for s in sorted(all_strings):
            f.write(s + '\n')
    print(f"  Saved to: {strings_file}")
    
    # Look for password-like strings
    print("\n[4] FINDING PASSWORD CANDIDATES")
    password_candidates = []
    for s in all_strings:
        if 6 <= len(s) <= 15:
            if s.replace('_', '').isalnum():
                has_upper = any(c.isupper() for c in s)
                has_lower = any(c.islower() for c in s)
                has_digit = any(c.isdigit() for c in s)
                
                if (has_upper and has_lower) or (has_digit and (has_upper or has_lower)):
                    if s not in ['String', 'Object', 'Class', 'Method', 'Boolean', 
                                 'Integer', 'Double', 'Float', 'android', 'Activity']:
                        password_candidates.append(s)
    
    print(f"  Found {len(password_candidates)} password candidates")
    
    # Filter for ones with 'raj' or similar
    raj_related = [s for s in password_candidates if 'raj' in s.lower() or 'aj' in s.lower()]
    
    print(f"\n  Password candidates with 'raj' or 'aj':")
    for s in sorted(set(raj_related)):
        print(f"    {s}")
    
    # Save password candidates
    pwd_file = os.path.join(OUTPUT_DIR, "password_candidates.txt")
    with open(pwd_file, 'w') as f:
        for s in sorted(set(password_candidates)):
            f.write(s + '\n')
    print(f"\n  All candidates saved to: {pwd_file}")
    
    # Look for the actual password validation code
    print("\n[5] SEARCHING FOR PASSWORD VALIDATION")
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            
            # Look for the toast message and nearby code
            if b'Password Is Near RAJ' in content:
                print(f"  Found toast in {name}")
                pos = content.find(b'Password Is Near RAJ')
                
                # Get a large context
                context = content[max(0, pos-500):pos+500]
                
                # Look for strings that might be the password
                nearby_strings = re.findall(rb'[\x20-\x7e]{5,20}\x00', context)
                print(f"  Strings near toast message:")
                for s in nearby_strings:
                    try:
                        decoded = s[:-1].decode('utf-8')
                        if 6 <= len(decoded) <= 15 and decoded.replace('_', '').isalnum():
                            print(f"    >>> {decoded}")
                    except:
                        pass

print("\n" + "="*80)
print(f"\nAll files extracted to: {OUTPUT_DIR}/")
print("Check password_candidates.txt for all possible passwords")
print("="*80)
