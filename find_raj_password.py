#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find RAJ password in APK
"""
import zipfile
import re
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

APK_PATH = "D:\\mission-git-hackss\\KaalRaj.apk"

print("="*80)
print("FINDING RAJ PASSWORD IN APK")
print("="*80)

print("\nHint: 'Password Is Near RAJ But Raj Is Lost In Code So Find Raj'")
print("Looking for RAJ-related strings in the APK...")

try:
    with zipfile.ZipFile(APK_PATH, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        print(f"\nTotal files: {len(file_list)}")
        
        # Search in all DEX files
        print("\n[Searching in DEX files]")
        for file in file_list:
            if file.endswith('.dex'):
                print(f"\nChecking: {file}")
                content = zip_ref.read(file)
                
                # Extract strings
                strings = re.findall(b'[\x20-\x7e]{4,}', content)
                
                raj_strings = []
                password_strings = []
                
                for s in strings:
                    try:
                        text = s.decode('utf-8')
                        if 'raj' in text.lower():
                            raj_strings.append(text)
                        if 'password' in text.lower():
                            password_strings.append(text)
                        if 'Kaal{' in text:
                            print(f"  [FLAG FOUND]: {text}")
                    except:
                        pass
                
                # Show RAJ-related strings
                if raj_strings:
                    print(f"  RAJ-related strings ({len(raj_strings)}):")
                    unique_raj = list(set(raj_strings))[:20]
                    for s in unique_raj:
                        print(f"    {s}")
                
                # Show password-related strings
                if password_strings:
                    print(f"  Password-related strings ({len(password_strings)}):")
                    unique_pass = list(set(password_strings))[:20]
                    for s in unique_pass:
                        print(f"    {s}")
        
        # Check AndroidManifest.xml
        print("\n[Checking AndroidManifest.xml]")
        try:
            manifest = zip_ref.read('AndroidManifest.xml')
            # Try to find readable strings
            strings = re.findall(b'[\x20-\x7e]{4,}', manifest)
            for s in strings:
                try:
                    text = s.decode('utf-8')
                    if 'raj' in text.lower() or 'password' in text.lower():
                        print(f"  {text}")
                except:
                    pass
        except:
            pass
        
        # Check resources
        print("\n[Checking resources]")
        for file in file_list:
            if 'res/' in file and file.endswith('.xml'):
                try:
                    content = zip_ref.read(file)
                    strings = re.findall(b'[\x20-\x7e]{4,}', content)
                    for s in strings:
                        try:
                            text = s.decode('utf-8')
                            if 'raj' in text.lower() or 'password' in text.lower():
                                print(f"  {file}: {text}")
                        except:
                            pass
                except:
                    pass

except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
