#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep search for RAJ and complete flag
"""
import zipfile
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

APK_PATH = "D:\\mission-git-hackss\\KaalRaj.apk"

print("="*80)
print("DEEP SEARCH FOR RAJ AND FLAG")
print("="*80)

try:
    with zipfile.ZipFile(APK_PATH, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        
        # Search for complete Kaal{ flags
        print("\n[Searching for complete flags]")
        for file in file_list:
            if file.endswith('.dex'):
                content = zip_ref.read(file)
                
                # Look for Kaal{ pattern with more context
                matches = re.finditer(b'Kaal\{[^}]{1,100}\}', content)
                for match in matches:
                    try:
                        flag = match.group(0).decode('utf-8')
                        print(f"  {file}: {flag}")
                    except:
                        pass
                
                # Also look for partial flags that might be split
                kaal_positions = [m.start() for m in re.finditer(b'Kaal\{', content)]
                for pos in kaal_positions:
                    context = content[pos:pos+200]
                    try:
                        text = context.decode('utf-8', errors='ignore')
                        print(f"  {file} at {pos}: {text[:100]}")
                    except:
                        pass
        
        # Search for "raj" with context
        print("\n[Searching for 'raj' with context]")
        for file in file_list:
            if file.endswith('.dex'):
                content = zip_ref.read(file)
                
                # Find all occurrences of 'raj' (case insensitive)
                raj_positions = []
                for match in re.finditer(b'[Rr][Aa][Jj]', content):
                    raj_positions.append(match.start())
                
                if raj_positions:
                    print(f"\n  {file}: Found {len(raj_positions)} 'raj' occurrences")
                    for pos in raj_positions[:10]:  # Show first 10
                        context = content[max(0, pos-50):pos+50]
                        try:
                            text = context.decode('utf-8', errors='ignore')
                            print(f"    ...{text}...")
                        except:
                            pass
        
        # Look for embedded APK (the second app)
        print("\n[Looking for embedded APK]")
        for file in file_list:
            if file.endswith('.apk') or 'apk' in file.lower():
                print(f"  Found: {file}")
                # Extract and analyze it
                try:
                    embedded_apk = zip_ref.read(file)
                    print(f"    Size: {len(embedded_apk)} bytes")
                    
                    # Search for flag in embedded APK
                    flags = re.findall(b'Kaal\{[^}]+\}', embedded_apk)
                    for flag in flags:
                        try:
                            print(f"    FLAG: {flag.decode('utf-8')}")
                        except:
                            pass
                except Exception as e:
                    print(f"    Error: {e}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
