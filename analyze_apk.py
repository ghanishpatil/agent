#!/usr/bin/env python3
"""
Analyze the KaalRaj.apk file
"""
import zipfile
import os
import re

APK_PATH = "KaalRaj.apk"

print("="*80)
print("ANALYZING KAALRAJ.APK")
print("="*80)

if not os.path.exists(APK_PATH):
    print(f"\n✗ APK file not found: {APK_PATH}")
    print("Please download the APK and place it in the current directory")
    exit(1)

print(f"\n[APK Info]")
print(f"File: {APK_PATH}")
print(f"Size: {os.path.getsize(APK_PATH)} bytes ({os.path.getsize(APK_PATH)/1024/1024:.2f} MB)")

# Extract APK (it's just a ZIP file)
print(f"\n[Extracting APK contents]")
extract_dir = "KaalRaj_extracted"

try:
    with zipfile.ZipFile(APK_PATH, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"✓ Extracted to: {extract_dir}")
except Exception as e:
    print(f"✗ Error extracting: {e}")
    exit(1)

# List all files
print(f"\n[Files in APK]")
all_files = []
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        filepath = os.path.join(root, file)
        all_files.append(filepath)

print(f"Total files: {len(all_files)}")

# Look for interesting files
print(f"\n[Interesting files]")
interesting_patterns = [
    r'\.dex$',
    r'\.so$',
    r'\.xml$',
    r'flag',
    r'secret',
    r'key',
    r'config',
    r'\.txt$',
    r'\.json$',
]

for pattern in interesting_patterns:
    matches = [f for f in all_files if re.search(pattern, f, re.IGNORECASE)]
    if matches:
        print(f"\n  Pattern: {pattern}")
        for match in matches[:10]:
            size = os.path.getsize(match)
            print(f"    {match} ({size} bytes)")

# Look for strings containing "Kaal" or "flag"
print(f"\n[Searching for flags in text files]")
text_extensions = ['.txt', '.xml', '.json', '.properties', '.cfg', '.conf']

for filepath in all_files:
    if any(filepath.endswith(ext) for ext in text_extensions):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'Kaal{' in content or 'flag' in content.lower():
                    print(f"\n  ✓ {filepath}")
                    # Extract flag
                    flags = re.findall(r'Kaal\{[^}]+\}', content)
                    if flags:
                        print(f"    FLAGS FOUND: {flags}")
                    else:
                        # Show context
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'flag' in line.lower():
                                print(f"    Line {i}: {line[:100]}")
        except:
            pass

# Check for hidden files in assets or resources
print(f"\n[Checking assets and resources]")
asset_dirs = ['assets', 'res', 'resources']
for asset_dir in asset_dirs:
    asset_path = os.path.join(extract_dir, asset_dir)
    if os.path.exists(asset_path):
        print(f"\n  {asset_dir}:")
        for root, dirs, files in os.walk(asset_path):
            for file in files:
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                print(f"    {filepath} ({size} bytes)")

print("\n" + "="*80)
print("Next steps:")
print("1. Decompile DEX files using jadx or apktool")
print("2. Check AndroidManifest.xml for permissions and activities")
print("3. Look for hidden payloads in native libraries (.so files)")
print("4. Search for embedded files or encrypted data")
print("="*80)
