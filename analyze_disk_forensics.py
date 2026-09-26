#!/usr/bin/env python3
"""
Forensics challenge - analyze disk image for hidden data
"""
import os
import subprocess
import re

disk_path = "disk1_extracted/disk/Disk2.001"

print(f"[*] Analyzing disk image: {disk_path}")
print(f"[*] File size: {os.path.getsize(disk_path)} bytes")

# Check file type
print("\n[*] File type analysis:")
result = subprocess.run(['file', disk_path], capture_output=True, text=True)
print(result.stdout)

# Try to mount or analyze as filesystem
print("\n[*] Checking for filesystem signatures...")

# Read first few KB to check for magic bytes
with open(disk_path, 'rb') as f:
    header = f.read(4096)
    print(f"First 512 bytes (hex):")
    print(header[:512].hex())
    
    # Look for common filesystem signatures
    if b'NTFS' in header:
        print("\n[+] NTFS filesystem detected!")
    elif header[510:512] == b'\x55\xaa':
        print("\n[+] MBR boot signature detected!")
    elif b'EXT' in header[:1024]:
        print("\n[+] EXT filesystem detected!")
    
    # Search for flag patterns
    print("\n[*] Searching for flag patterns in first 4KB...")
    if b'Kaal{' in header:
        print("[+] Found flag pattern in header!")
        idx = header.find(b'Kaal{')
        print(f"Flag preview: {header[idx:idx+50]}")

# Try strings command to find readable text
print("\n[*] Running strings analysis...")
result = subprocess.run(['strings', disk_path], capture_output=True, text=True)
strings_output = result.stdout

# Search for Kaal{ flag
flags = re.findall(r'Kaal\{[^}]+\}', strings_output)
if flags:
    print(f"\n[+] Found {len(flags)} potential flag(s):")
    for flag in flags:
        print(f"    {flag}")
else:
    print("\n[-] No obvious flags found in strings")
    
# Look for interesting strings
print("\n[*] Interesting strings (first 50):")
lines = strings_output.split('\n')
for i, line in enumerate(lines[:50]):
    if line.strip():
        print(f"  {line}")

print("\n[*] Checking for hidden/deleted files...")
