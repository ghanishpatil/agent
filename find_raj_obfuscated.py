#!/usr/bin/env python3
"""Find RAJ that might be obfuscated or split"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("FINDING OBFUSCATED RAJ")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            
            # Find all strings
            all_strings = []
            for match in re.finditer(rb'[\x20-\x7e]{2,50}\x00', content):
                try:
                    s = match.group()[:-1].decode('utf-8')
                    all_strings.append(s)
                except:
                    pass
            
            print(f"\n[{name}]")
            
            # Look for strings that might hide RAJ
            # 1. Strings with R, A, J in them
            raj_hidden = []
            for s in all_strings:
                # Check if string contains R, A, J in order (but not necessarily together)
                if 'R' in s and 'A' in s and 'J' in s:
                    r_pos = s.index('R')
                    a_pos = s.index('A', r_pos)
                    try:
                        j_pos = s.index('J', a_pos)
                        if j_pos - r_pos <= 10:  # Within 10 chars
                            raj_hidden.append(s)
                    except:
                        pass
            
            if raj_hidden:
                print(f"\nStrings with R-A-J pattern:")
                for s in set(raj_hidden[:20]):
                    print(f"  {s}")
            
            # 2. Look for class/method names with RAJ
            class_method_names = [s for s in all_strings if len(s) > 3 and s[0].isupper()]
            raj_in_names = [s for s in class_method_names if 'RAJ' in s or 'Raj' in s]
            
            if raj_in_names:
                print(f"\nClass/method names with RAJ:")
                for s in set(raj_in_names[:20]):
                    print(f"  {s}")
            
            # 3. Look for strings that are exactly 7-10 chars and alphanumeric
            # (typical password length)
            potential_passwords = []
            for s in all_strings:
                if 7 <= len(s) <= 10:
                    if s.isalnum():
                        # Check if it has mixed case or numbers
                        has_upper = any(c.isupper() for c in s)
                        has_lower = any(c.islower() for c in s)
                        has_digit = any(c.isdigit() for c in s)
                        
                        if (has_upper and has_lower) or (has_digit and (has_upper or has_lower)):
                            potential_passwords.append(s)
            
            if potential_passwords:
                print(f"\nPotential passwords (7-10 chars, mixed case/numbers):")
                for s in set(potential_passwords[:30]):
                    print(f"  {s}")

print("\n" + "="*80)
