#!/usr/bin/env python3
"""Extract and analyze the embedded APK"""
import zipfile
import re
import os

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("EXTRACTING EMBEDDED APK")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    # Find the file with the long Arabic name
    for name in z.namelist():
        if name.startswith('assets/') and len(name) > 100:
            print(f"\nFound embedded file: {name[:50]}...")
            print(f"Full length: {len(name)} characters")
            
            # Extract it
            embedded_data = z.read(name)
            print(f"Size: {len(embedded_data)} bytes")
            
            # Check if it's an APK (starts with PK)
            if embedded_data[:2] == b'PK':
                print("This is a ZIP/APK file!")
                
                # Save it
                output_path = "embedded_app.apk"
                with open(output_path, 'wb') as f:
                    f.write(embedded_data)
                print(f"Saved to: {output_path}")
                
                # Search for flags in the embedded APK
                print("\n[Searching embedded APK for flags]")
                flags = re.findall(rb'Kaal\{[^}]+\}', embedded_data)
                if flags:
                    print("Found flags:")
                    for flag in set(flags):
                        print(f"  {flag.decode('utf-8', errors='ignore')}")
                
                # Search for password-related strings
                print("\n[Searching for password]")
                password_patterns = [
                    rb'password["\s:=]+([A-Za-z0-9_]+)',
                    rb'pass["\s:=]+([A-Za-z0-9_]+)',
                    rb'RAJ[A-Za-z0-9_]+',
                    rb'raj[0-9]+',
                ]
                
                for pattern in password_patterns:
                    matches = re.findall(pattern, embedded_data, re.IGNORECASE)
                    if matches:
                        print(f"Pattern {pattern}:")
                        for m in set(matches[:10]):
                            try:
                                print(f"  {m.decode('utf-8', errors='ignore')}")
                            except:
                                print(f"  {m}")
                
                # Now analyze the embedded APK as a ZIP
                print("\n[Analyzing embedded APK structure]")
                try:
                    with zipfile.ZipFile(output_path, 'r') as embedded_zip:
                        print(f"Files in embedded APK: {len(embedded_zip.namelist())}")
                        
                        # Search DEX files
                        for dex_name in embedded_zip.namelist():
                            if dex_name.endswith('.dex'):
                                print(f"\nSearching {dex_name}...")
                                dex_content = embedded_zip.read(dex_name)
                                
                                # Search for flags
                                flags = re.findall(rb'Kaal\{[^}]+\}', dex_content)
                                if flags:
                                    print(f"  Flags found:")
                                    for flag in set(flags):
                                        print(f"    {flag.decode('utf-8', errors='ignore')}")
                                
                                # Search for RAJ
                                raj_matches = re.findall(rb'RAJ[A-Za-z0-9_]{1,20}', dex_content)
                                if raj_matches:
                                    print(f"  RAJ strings:")
                                    for m in set(raj_matches[:10]):
                                        print(f"    {m.decode('utf-8', errors='ignore')}")
                except Exception as e:
                    print(f"Error analyzing embedded APK: {e}")
            else:
                print(f"Not a ZIP/APK file. First bytes: {embedded_data[:10]}")

print("\n" + "="*80)
