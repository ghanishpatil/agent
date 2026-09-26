#!/usr/bin/env python3
"""Aggressively find the password"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("AGGRESSIVE PASSWORD SEARCH")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            
            # The hint says: "Password Is Near RAJ But Raj Is Lost In Code So Find Raj"
            # Look for any string with RAJ or raj
            
            print(f"\n[{name}]")
            
            # Pattern 1: Exact RAJ followed by numbers/letters
            raj_patterns = [
                rb'RAJ[0-9]+',
                rb'raj[0-9]+',
                rb'Raj[0-9]+',
                rb'[A-Z]*RAJ[A-Z0-9]*',
                rb'[a-z]*raj[a-z0-9]*',
            ]
            
            for pattern in raj_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    unique = set(matches)
                    print(f"\nPattern {pattern}:")
                    for m in unique:
                        try:
                            decoded = m.decode('utf-8')
                            # Filter out very long strings (likely not passwords)
                            if 3 <= len(decoded) <= 20:
                                print(f"  {decoded}")
                        except:
                            pass
            
            # Pattern 2: Look for strings that contain "raj" case-insensitive
            # and are reasonable password length
            all_strings = re.findall(rb'[A-Za-z][A-Za-z0-9_]{4,15}', content)
            raj_strings = []
            for s in all_strings:
                try:
                    decoded = s.decode('utf-8')
                    if 'raj' in decoded.lower():
                        raj_strings.append(decoded)
                except:
                    pass
            
            if raj_strings:
                print(f"\nStrings containing 'raj':")
                for s in set(raj_strings[:30]):
                    print(f"  {s}")
            
            # Pattern 3: Look near the author name "raj045735"
            if b'raj045735' in content or b'045735' in content:
                print(f"\nFound author reference!")
                pos = content.find(b'raj045735') if b'raj045735' in content else content.find(b'045735')
                context = content[max(0, pos-100):pos+100]
                strings = re.findall(rb'[A-Za-z0-9_]{5,20}', context)
                print("Nearby strings:")
                for s in strings:
                    try:
                        print(f"  {s.decode('utf-8')}")
                    except:
                        pass

print("\n" + "="*80)
print("\nMOST LIKELY PASSWORDS TO TRY:")
print("1. raj045735 (author name)")
print("2. VurrAj0 (found in code)")
print("3. raj (simple)")
print("4. RAJ (uppercase)")
print("5. Raj (capitalized)")
print("6. Any other raj-related string found above")
print("="*80)
