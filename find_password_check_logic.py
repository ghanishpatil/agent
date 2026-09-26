#!/usr/bin/env python3
"""Find the actual password checking logic"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("FINDING PASSWORD CHECK LOGIC")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            
            # Look for password checking patterns
            # Common patterns: equals, check, verify, getText, toString
            
            # Find strings that look like they're being compared
            # Look for patterns like: "somestring".equals(input)
            
            # Search for the toast message we saw
            if b'Password Is Near RAJ' in content:
                print(f"\n[Found toast message in {name}]")
                pos = content.find(b'Password Is Near RAJ')
                context = content[max(0, pos-200):pos+200]
                
                # Look for strings nearby
                strings = re.findall(rb'[A-Za-z0-9_]{4,20}', context)
                print("Strings near toast message:")
                for s in set(strings):
                    try:
                        decoded = s.decode('utf-8')
                        print(f"  {decoded}")
                    except:
                        pass
            
            # Look for "Enter Wrong Password" message
            if b'Enter Wrong Password' in content or b'Wrong Password' in content:
                print(f"\n[Found wrong password message in {name}]")
                pos = content.find(b'Enter Wrong Password' if b'Enter Wrong Password' in content else b'Wrong Password')
                context = content[max(0, pos-200):pos+200]
                
                strings = re.findall(rb'[A-Za-z0-9_]{4,20}', context)
                print("Strings near wrong password message:")
                for s in set(strings):
                    try:
                        decoded = s.decode('utf-8')
                        print(f"  {decoded}")
                    except:
                        pass
            
            # Look for common password validation strings
            validation_keywords = [
                b'correct',
                b'Correct',
                b'CORRECT',
                b'success',
                b'Success',
                b'SUCCESS',
                b'valid',
                b'Valid',
                b'VALID',
            ]
            
            for keyword in validation_keywords:
                if keyword in content:
                    print(f"\n[Found '{keyword.decode()}' in {name}]")
                    pos = content.find(keyword)
                    context = content[max(0, pos-100):pos+100]
                    strings = re.findall(rb'[A-Za-z0-9_]{4,20}', context)
                    print(f"Nearby strings:")
                    for s in set(strings[:15]):
                        try:
                            decoded = s.decode('utf-8')
                            if decoded not in ['android', 'String', 'Object', 'Class']:
                                print(f"  {decoded}")
                        except:
                            pass

print("\n" + "="*80)
