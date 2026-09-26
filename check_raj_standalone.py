#!/usr/bin/env python3
"""Check what's near the standalone RAJ string"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("CHECKING STANDALONE RAJ")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            
            # Find all strings
            all_strings = []
            for match in re.finditer(rb'[\x20-\x7e]{3,50}\x00', content):
                try:
                    s = match.group()[:-1].decode('utf-8')
                    all_strings.append((match.start(), match.end(), s))
                except:
                    pass
            
            # Find the standalone "RAJ" string
            raj_strings = [(pos, end, s) for pos, end, s in all_strings if s == 'RAJ']
            
            if raj_strings:
                print(f"\n[{name}] Found standalone 'RAJ' string")
                for pos, end, s in raj_strings:
                    print(f"\nPosition {pos}: '{s}'")
                    
                    # Find strings immediately before and after
                    # Look within 50 bytes
                    nearby_before = [(p, e, st) for p, e, st in all_strings if e <= pos and e > pos - 50]
                    nearby_after = [(p, e, st) for p, e, st in all_strings if p >= end and p < end + 50]
                    
                    if nearby_before:
                        print(f"  Strings BEFORE:")
                        for p, e, st in nearby_before[-3:]:  # Last 3
                            print(f"    {st}")
                    
                    if nearby_after:
                        print(f"  Strings AFTER:")
                        for p, e, st in nearby_after[:3]:  # First 3
                            print(f"    {st}")
                    
                    # Also check what's in the immediate bytes after RAJ
                    immediate_after = content[end:end+30]
                    print(f"  Immediate bytes after: {immediate_after[:30]}")
                    
                    # Try to extract any readable string
                    readable = re.findall(rb'[A-Za-z0-9_]{4,20}', immediate_after)
                    if readable:
                        print(f"  Readable strings after RAJ:")
                        for r in readable:
                            print(f"    >>> {r.decode('utf-8')} <<<")

print("\n" + "="*80)
print("\nBASED ON ANALYSIS:")
print("The password is likely: VurrAj0")
print("(Found in set-VurrAj0, and contains 'Aj' related to RAJ)")
print("="*80)
