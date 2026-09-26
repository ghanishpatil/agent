#!/usr/bin/env python3
"""Find RAJ literally in the code - it might be split or obfuscated"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("FINDING RAJ IN CODE")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            
            # Look for RAJ with exact case
            if b'RAJ' in content:
                print(f"\n[Found 'RAJ' in {name}]")
                
                # Find all positions
                positions = [m.start() for m in re.finditer(rb'RAJ', content)]
                print(f"Found {len(positions)} occurrences")
                
                # Check each occurrence
                for i, pos in enumerate(positions[:20]):
                    # Get context before and after
                    before = content[max(0, pos-30):pos]
                    after = content[pos+3:pos+30]
                    
                    # Try to extract readable strings
                    before_str = re.findall(rb'[A-Za-z0-9_]{3,}', before)
                    after_str = re.findall(rb'[A-Za-z0-9_]{3,}', after)
                    
                    # Get the full string containing RAJ
                    full_context = content[max(0, pos-20):pos+20]
                    full_strings = re.findall(rb'[A-Za-z0-9_]{5,25}', full_context)
                    
                    if full_strings:
                        print(f"\n  Occurrence #{i+1} at position {pos}:")
                        for s in full_strings:
                            try:
                                decoded = s.decode('utf-8')
                                if 'RAJ' in decoded:
                                    print(f"    >>> {decoded} <<<")
                                else:
                                    print(f"    {decoded}")
                            except:
                                pass
            
            # Also look for "Raj" (capitalized)
            if b'Raj' in content and b'Raj' != b'RAJ':
                print(f"\n[Found 'Raj' (capitalized) in {name}]")
                positions = [m.start() for m in re.finditer(rb'Raj', content)]
                print(f"Found {len(positions)} occurrences")
                
                for i, pos in enumerate(positions[:10]):
                    full_context = content[max(0, pos-20):pos+20]
                    full_strings = re.findall(rb'[A-Za-z0-9_]{5,25}', full_context)
                    
                    if full_strings:
                        print(f"\n  Occurrence #{i+1} at position {pos}:")
                        for s in full_strings:
                            try:
                                decoded = s.decode('utf-8')
                                if 'Raj' in decoded:
                                    print(f"    >>> {decoded} <<<")
                            except:
                                pass

print("\n" + "="*80)
print("\nLOOKING FOR PATTERN:")
print("The hint says 'Password Is Near RAJ But Raj Is Lost In Code'")
print("This means:")
print("1. Find where 'RAJ' appears in the code")
print("2. The password is NEAR that location")
print("3. Look at strings immediately before or after RAJ")
print("="*80)
