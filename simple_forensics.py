#!/usr/bin/env python3
"""
Simple forensics - use basic techniques to find hidden data
"""
import os
import subprocess

disk_path = "disk1_extracted/disk/Disk2.001"

print("[*] Forensics Challenge - Disk Image Analysis")
print(f"[*] Target: {disk_path}")
print(f"[*] Size: {os.path.getsize(disk_path):,} bytes\n")

# 1. Check if we can use FTK Imager or similar
print("[1] Trying to use AccessData FTK Imager (if installed)...")

# 2. Use binwalk to find embedded files
print("\n[2] Using binwalk to find embedded files...")
try:
    result = subprocess.run(['binwalk', '-e', disk_path], capture_output=True, text=True)
    print(result.stdout)
except FileNotFoundError:
    print("[-] binwalk not found")

# 3. Use foremost for file carving
print("\n[3] Using foremost for file carving...")
try:
    os.makedirs("foremost_output", exist_ok=True)
    result = subprocess.run(['foremost', '-i', disk_path, '-o', 'foremost_output'], 
                          capture_output=True, text=True)
    print(result.stdout)
except FileNotFoundError:
    print("[-] foremost not found")

# 4. Use scalpel for file carving
print("\n[4] Using scalpel for file carving...")
try:
    os.makedirs("scalpel_output", exist_ok=True)
    result = subprocess.run(['scalpel', disk_path, '-o', 'scalpel_output'], 
                          capture_output=True, text=True)
    print(result.stdout)
except FileNotFoundError:
    print("[-] scalpel not found")

# 5. Simple hex dump and grep for flag
print("\n[5] Searching for 'Kaal{' in hex dump...")
try:
    # Use PowerShell Select-String on Windows
    cmd = f'Select-String -Path "{disk_path}" -Pattern "Kaal" -Encoding Byte'
    result = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True)
    if result.stdout:
        print("[+] Found matches:")
        print(result.stdout[:1000])
except Exception as e:
    print(f"[-] Error: {e}")

print("\n[*] Check the output directories for carved files!")
print("[*] Look in: foremost_output/ and scalpel_output/")
