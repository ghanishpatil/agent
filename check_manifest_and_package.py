#!/usr/bin/env python3
"""Check manifest and package names"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("CHECKING MANIFEST AND PACKAGE")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    # Check AndroidManifest.xml
    try:
        manifest = z.read('AndroidManifest.xml')
        print("\n[AndroidManifest.xml]")
        print(f"Size: {len(manifest)} bytes")
        
        # Try to find readable strings
        strings = re.findall(rb'[\x20-\x7e]{4,}', manifest)
        print("\nReadable strings in manifest:")
        for s in strings[:50]:
            try:
                decoded = s.decode('utf-8')
                if len(decoded) > 3:
                    print(f"  {decoded}")
            except:
                pass
    except Exception as e:
        print(f"Error reading manifest: {e}")
    
    # Check for resources.arsc
    try:
        resources = z.read('resources.arsc')
        print(f"\n[resources.arsc]")
        print(f"Size: {len(resources)} bytes")
        
        # Look for strings
        strings = re.findall(rb'[\x20-\x7e]{5,50}', resources)
        print("\nStrings in resources (first 50):")
        for s in strings[:50]:
            try:
                decoded = s.decode('utf-8')
                print(f"  {decoded}")
            except:
                pass
    except Exception as e:
        print(f"Error reading resources: {e}")
    
    # List all files
    print(f"\n[APK Contents]")
    print(f"Total files: {len(z.namelist())}")
    
    # Look for interesting files
    interesting = [f for f in z.namelist() if 'password' in f.lower() or 'secret' in f.lower() or 'key' in f.lower()]
    if interesting:
        print("\nInteresting files:")
        for f in interesting:
            print(f"  {f}")

print("\n" + "="*80)
