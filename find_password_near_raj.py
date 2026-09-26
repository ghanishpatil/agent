#!/usr/bin/env python3
"""Find password near RAJ by looking at raw bytes"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("FINDING PASSWORD NEAR RAJ")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            
            if b'RAJ' in content:
                print(f"\n[Analyzing RAJ in {name}]")
                
                positions = [m.start() for m in re.finditer(rb'RAJ', content)]
                
                for i, pos in enumerate(positions):
                    print(f"\n--- RAJ Occurrence #{i+1} at position {pos} ---")
                    
                    # Get larger context
                    start = max(0, pos - 100)
                    end = min(len(content), pos + 100)
                    context = content[start:end]
                    
                    # Show raw bytes
                    print(f"Raw bytes around RAJ:")
                    print(context)
                    
                    # Try to find all printable strings in this context
                    print(f"\nPrintable strings:")
                    strings = re.findall(rb'[\x20-\x7e]{4,}', context)
                    for s in strings:
                        print(f"  {s.decode('utf-8')}")
                    
                    # Look for specific patterns that might be passwords
                    # Pattern: alphanumeric, 6-20 chars
                    passwords = re.findall(rb'[A-Za-z][A-Za-z0-9]{5,19}', context)
                    if passwords:
                        print(f"\nPotential passwords:")
                        for p in set(passwords):
                            try:
                                decoded = p.decode('utf-8')
                                # Filter out common words
                                if decoded not in ['android', 'String', 'Object', 'Class', 'Method']:
                                    print(f"  >>> {decoded}")
                            except:
                                pass

print("\n" + "="*80)
