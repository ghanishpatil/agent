#!/usr/bin/env python3
"""
Search for strings in APK files including DEX and SO files
"""
import os
import re
import subprocess

APK_PATH = "KaalRaj.apk"
EXTRACT_DIR = "KaalRaj_extracted"

print("="*80)
print("SEARCHING FOR STRINGS IN APK")
print("="*80)

if not os.path.exists(EXTRACT_DIR):
    print(f"✗ Extracted directory not found. Run analyze_apk.py first")
    exit(1)

# Search for "Kaal{" pattern in all files
print(f"\n[Searching for flag pattern in all files]")

def search_in_file(filepath):
    """Search for flag patterns in a file"""
    try:
        # Try as text first
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            flags = re.findall(r'Kaal\{[^}]+\}', content)
            if flags:
                return flags
        
        # Try as binary
        with open(filepath, 'rb') as f:
            content = f.read()
            # Look for Kaal{ pattern in bytes
            if b'Kaal{' in content:
                # Extract surrounding context
                idx = content.find(b'Kaal{')
                context = content[idx:idx+100]
                try:
                    text = context.decode('utf-8', errors='ignore')
                    flags = re.findall(r'Kaal\{[^}]+\}', text)
                    if flags:
                        return flags
                except:
                    pass
    except:
        pass
    return None

# Search all files
for root, dirs, files in os.walk(EXTRACT_DIR):
    for file in files:
        filepath = os.path.join(root, file)
        flags = search_in_file(filepath)
        if flags:
            print(f"\n✓ Found in: {filepath}")
            for flag in flags:
                print(f"  FLAG: {flag}")

# Use strings command if available (on Linux/Mac)
print(f"\n[Using strings command on DEX files]")
dex_files = []
for root, dirs, files in os.walk(EXTRACT_DIR):
    for file in files:
        if file.endswith('.dex'):
            dex_files.append(os.path.join(root, file))

for dex_file in dex_files:
    print(f"\n  Checking: {dex_file}")
    try:
        # Try using strings command
        result = subprocess.run(['strings', dex_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        output = result.stdout
        
        # Search for flag
        flags = re.findall(r'Kaal\{[^}]+\}', output)
        if flags:
            print(f"    ✓ FLAGS: {flags}")
        
        # Look for interesting strings
        lines = output.split('\n')
        for line in lines:
            if 'flag' in line.lower() or 'secret' in line.lower() or 'key' in line.lower():
                print(f"    {line}")
    except:
        # strings command not available, read manually
        try:
            with open(dex_file, 'rb') as f:
                content = f.read()
                # Simple string extraction
                strings = re.findall(b'[\x20-\x7e]{4,}', content)
                for s in strings:
                    try:
                        text = s.decode('utf-8')
                        if 'Kaal{' in text:
                            print(f"    ✓ {text}")
                    except:
                        pass
        except:
            pass

print("\n" + "="*80)
