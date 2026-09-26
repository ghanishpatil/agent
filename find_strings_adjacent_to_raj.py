#!/usr/bin/env python3
"""Find strings immediately adjacent to RAJ"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("FINDING STRINGS ADJACENT TO RAJ")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            
            # Find all strings (null-terminated)
            # DEX format stores strings as length-prefixed, null-terminated
            all_strings = []
            
            # Simple approach: find sequences of printable ASCII followed by null
            for match in re.finditer(rb'[\x20-\x7e]{3,50}\x00', content):
                try:
                    s = match.group()[:-1].decode('utf-8')  # Remove null byte
                    all_strings.append((match.start(), s))
                except:
                    pass
            
            print(f"\n[{name}] Found {len(all_strings)} strings")
            
            # Now find strings that contain or are near RAJ
            raj_related = []
            for pos, s in all_strings:
                if 'RAJ' in s or 'raj' in s.lower():
                    raj_related.append((pos, s))
            
            if raj_related:
                print(f"\nStrings containing RAJ/raj:")
                for pos, s in raj_related:
                    print(f"  Position {pos}: {s}")
                    
                    # Find the next string after this one
                    next_strings = [x for x in all_strings if x[0] > pos and x[0] < pos + 100]
                    if next_strings:
                        print(f"    Next string: {next_strings[0][1]}")
                    
                    # Find the previous string
                    prev_strings = [x for x in all_strings if x[0] < pos and x[0] > pos - 100]
                    if prev_strings:
                        print(f"    Previous string: {prev_strings[-1][1]}")

print("\n" + "="*80)
