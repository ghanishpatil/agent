#!/usr/bin/env python3
"""
Forensics challenge - analyze disk image for hidden data
"""
import os
import re

disk_path = "disk1_extracted/disk/Disk2.001"

print(f"[*] Analyzing disk image: {disk_path}")
print(f"[*] File size: {os.path.getsize(disk_path):,} bytes (~1.5 GB)")

# Read header to check for filesystem signatures
print("\n[*] Checking filesystem signatures...")
with open(disk_path, 'rb') as f:
    header = f.read(4096)
    
    print(f"\n[*] First 128 bytes (hex):")
    for i in range(0, min(128, len(header)), 16):
        hex_str = ' '.join(f'{b:02x}' for b in header[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in header[i:i+16])
        print(f"  {i:04x}: {hex_str:<48} {ascii_str}")
    
    # Check for boot signature
    if header[510:512] == b'\x55\xaa':
        print("\n[+] MBR boot signature (0x55AA) detected at offset 510!")
    
    # Check for filesystem types
    if b'NTFS' in header[:1024]:
        print("[+] NTFS filesystem detected!")
    elif b'FAT' in header[:512]:
        print("[+] FAT filesystem detected!")
    elif b'EXT' in header[:1024]:
        print("[+] EXT filesystem detected!")

# Search for flag in entire file (this might take a while for 1.5GB)
print("\n[*] Searching for 'Kaal{' flag pattern in disk image...")
print("[*] This may take a few minutes for large files...")

chunk_size = 1024 * 1024  # 1MB chunks
found_flags = []
offset = 0

with open(disk_path, 'rb') as f:
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        
        # Search for Kaal{ pattern
        if b'Kaal{' in chunk:
            # Find all occurrences in this chunk
            idx = 0
            while True:
                idx = chunk.find(b'Kaal{', idx)
                if idx == -1:
                    break
                
                # Extract potential flag (up to 200 bytes)
                flag_data = chunk[idx:idx+200]
                # Try to find the closing brace
                end_idx = flag_data.find(b'}')
                if end_idx != -1:
                    flag = flag_data[:end_idx+1].decode('utf-8', errors='ignore')
                    found_flags.append((offset + idx, flag))
                    print(f"\n[+] Found flag at offset {offset + idx}: {flag}")
                
                idx += 1
        
        offset += len(chunk)
        if offset % (100 * 1024 * 1024) == 0:  # Progress every 100MB
            print(f"[*] Scanned {offset // (1024*1024)} MB...")

if found_flags:
    print(f"\n[+] Total flags found: {len(found_flags)}")
    for off, flag in found_flags:
        print(f"  Offset {off}: {flag}")
else:
    print("\n[-] No flags found with simple search")
    print("[*] Trying alternative approaches...")
    
    # Try looking for common file signatures
    print("\n[*] Searching for embedded files (ZIP, PNG, PDF, etc.)...")
    with open(disk_path, 'rb') as f:
        data = f.read(10 * 1024 * 1024)  # First 10MB
        
        signatures = {
            b'PK\x03\x04': 'ZIP',
            b'\x89PNG': 'PNG',
            b'%PDF': 'PDF',
            b'GIF8': 'GIF',
            b'\xff\xd8\xff': 'JPEG',
            b'RIFF': 'RIFF (WAV/AVI)',
        }
        
        for sig, name in signatures.items():
            if sig in data:
                idx = data.find(sig)
                print(f"[+] Found {name} signature at offset {idx}")

print("\n[*] Analysis complete!")
