#!/usr/bin/env python3
"""Smart password search"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("SMART PASSWORD SEARCH")
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
                    all_strings.append(s)
                except:
                    pass
            
            print(f"\n[{name}] - {len(all_strings)} strings")
            
            # Look for passwords: 6-12 chars, alphanumeric, mixed case or with numbers
            passwords = []
            for s in all_strings:
                if 6 <= len(s) <= 12 and s.replace('_', '').isalnum():
                    has_upper = any(c.isupper() for c in s)
                    has_lower = any(c.islower() for c in s)
                    has_digit = any(c.isdigit() for c in s)
                    
                    # Must have mixed case OR letters+numbers
                    if (has_upper and has_lower) or (has_digit and (has_upper or has_lower)):
                        # Filter out common words
                        if s not in ['String', 'Object', 'Class', 'Method', 'android', 
                                     'Boolean', 'Integer', 'Double', 'Float', 'Character',
                                     'Exception', 'Activity', 'Fragment', 'Context']:
                            passwords.append(s)
            
            if passwords:
                print(f"\nPassword candidates:")
                # Sort by likelihood (prefer shorter, with numbers)
                passwords_sorted = sorted(set(passwords), key=lambda x: (len(x), not any(c.isdigit() for c in x)))
                for p in passwords_sorted[:40]:
                    # Highlight if it contains raj-related
                    marker = " <<<" if 'raj' in p.lower() or 'aj' in p.lower() else ""
                    print(f"  {p}{marker}")

print("\n" + "="*80)
print("\nTRY THESE:")
print("1. Any password marked with <<<")
print("2. WpGqRn0")
print("3. raj045735")
print("="*80)
