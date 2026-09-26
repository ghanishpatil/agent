#!/usr/bin/env python3
"""Extract and analyze PyInstaller binary"""

import subprocess
import os
import sys

binary_path = r".\greetings\greetings"

print("=" * 60)
print("PYINSTALLER EXTRACTION")
print("=" * 60)

# Try pyinstxtractor
print("\n[*] Attempting to extract with pyinstxtractor...")
try:
    # Download pyinstxtractor if needed
    if not os.path.exists('pyinstxtractor.py'):
        print("    Downloading pyinstxtractor...")
        import urllib.request
        url = "https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py"
        urllib.request.urlretrieve(url, 'pyinstxtractor.py')
        print("    Downloaded!")
    
    # Extract
    result = subprocess.run([sys.executable, 'pyinstxtractor.py', binary_path], 
                          capture_output=True, text=True, timeout=30)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # Look for extracted files
    extracted_dir = binary_path + "_extracted"
    if os.path.exists(extracted_dir):
        print(f"\n[*] Files extracted to: {extracted_dir}")
        
        # Find the main pyc file
        for root, dirs, files in os.walk(extracted_dir):
            for file in files:
                if file.endswith('.pyc') or 'greetings' in file.lower():
                    filepath = os.path.join(root, file)
                    print(f"    Found: {filepath}")
                    
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "=" * 60)
