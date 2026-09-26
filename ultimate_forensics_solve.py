#!/usr/bin/env python3
"""
Ultimate forensics solution - try EVERYTHING
"""

import os
import struct
import re
import subprocess

mp3_file = "chall_media/chall_media.mp3"

with open(mp3_file, 'rb') as f:
    data = f.read()

print("="*70)
print("ULTIMATE FORENSICS ANALYSIS")
print("="*70)

# 1. Check file with strings command
print("\n[1] Running strings analysis...")
try:
    result = subprocess.run(['strings', mp3_file], capture_output=True, text=True, timeout=10)
    strings_output = result.stdout
    
    # Look for Kaal flags
    kaal_flags = re.findall(r'Kaal\{[^}]+\}', strings_output)
    if kaal_flags:
        print(f"[+] Flags found with strings:")
        for flag in kaal_flags:
            print(f"    {flag}")
    
    # Look for interesting strings
    interesting = []
    for line in strings_output.split('\n'):
        if any(keyword in line.lower() for keyword in ['flag', 'kaal', 'bheem', 'laddoo', 'key', 'password', 'hidden']):
            interesting.append(line)
    
    if interesting:
        print(f"\n[+] Interesting strings:")
        for s in interesting[:30]:
            print(f"    {s}")
            
except FileNotFoundError:
    print("[-] strings command not available")
except Exception as e:
    print(f"[-] Error: {e}")

# 2. Check with exiftool
print("\n[2] Checking metadata with exiftool...")
try:
    result = subprocess.run(['exiftool', mp3_file], capture_output=True, text=True, timeout=10)
    print(result.stdout)
    
    # Look for flag in metadata
    flags = re.findall(r'Kaal\{[^}]+\}', result.stdout)
    if flags:
        for flag in flags:
            if flag != 'Kaal{1_th1nk_th15_15_wr0ng}':
                print(f"\n[+] *** NEW FLAG IN METADATA ***: {flag}")
except FileNotFoundError:
    print("[-] exiftool not available")

# 3. Check with file command
print("\n[3] File type detection...")
try:
    result = subprocess.run(['file', mp3_file], capture_output=True, text=True)
    print(f"    {result.stdout}")
except:
    pass

# 4. Hexdump analysis - look at specific offsets
print("\n[4] Hexdump analysis of key areas...")

# Check first 512 bytes
print("\n    First 512 bytes:")
print(data[:512].hex())

# Check around the KEY marker
key_pos = data.find(b'KEY____________')
if key_pos != -1:
    print(f"\n    Around KEY marker (offset {key_pos}):")
    start = max(0, key_pos - 200)
    end = min(len(data), key_pos + 200)
    print(data[start:end])

# 5. Look for hidden ZIP with correct extraction
print("\n[5] Looking for hidden ZIP archives...")
zip_sig = b'PK\x03\x04'
zip_pos = data.find(zip_sig)

if zip_pos != -1 and zip_pos > 1000:
    print(f"[+] ZIP signature found at offset {zip_pos}")
    
    # Extract ZIP
    zip_data = data[zip_pos:]
    with open('hidden.zip', 'wb') as f:
        f.write(zip_data)
    
    print("    Saved as hidden.zip")
    
    # Try to extract
    import zipfile
    try:
        with zipfile.ZipFile('hidden.zip', 'r') as zf:
            print(f"    ZIP contents: {zf.namelist()}")
            
            # Try to extract with no password
            try:
                zf.extractall('hidden_zip_contents')
                print("    [+] Extracted successfully!")
                
                # Check all extracted files
                for filename in zf.namelist():
                    filepath = os.path.join('hidden_zip_contents', filename)
                    if os.path.isfile(filepath):
                        with open(filepath, 'rb') as f:
                            content = f.read()
                            print(f"\n    File: {filename}")
                            print(f"    Size: {len(content)} bytes")
                            print(f"    Content preview: {content[:200]}")
                            
                            # Look for flag
                            flags = re.findall(rb'Kaal\{[^}]+\}', content)
                            if flags:
                                for flag in flags:
                                    print(f"\n    [+] *** FLAG IN {filename} ***: {flag.decode('utf-8', errors='ignore')}")
            except RuntimeError as e:
                if 'password' in str(e).lower():
                    print("    ZIP is password protected!")
                    
                    # Try common passwords
                    passwords = [b'', b'bheem', b'laddoo', b'kalia', b'password', b'chhota', 
                                b'dholakpur', b'tuntun', b'mausi', b'WRONGKEY', b'recipe']
                    
                    for pwd in passwords:
                        try:
                            zf.extractall('hidden_zip_contents', pwd=pwd)
                            print(f"    [+] *** PASSWORD FOUND: {pwd.decode()} ***")
                            
                            # Check extracted files
                            for filename in zf.namelist():
                                filepath = os.path.join('hidden_zip_contents', filename)
                                if os.path.isfile(filepath):
                                    with open(filepath, 'rb') as f:
                                        content = f.read()
                                        print(f"\n    Extracted: {filename}")
                                        print(f"    Content: {content}")
                                        
                                        flags = re.findall(rb'Kaal\{[^}]+\}', content)
                                        if flags:
                                            for flag in flags:
                                                print(f"\n    [+] *** REAL FLAG ***: {flag.decode('utf-8', errors='ignore')}")
                            break
                        except:
                            continue
    except zipfile.BadZipFile:
        print("    Not a valid ZIP file")

# 6. Check for steganography with zsteg-like analysis
print("\n[6] Checking all possible LSB/MSB combinations...")

# Get audio data
data_pos = data.find(b'data')
if data_pos != -1:
    data_size = struct.unpack('<I', data[data_pos+4:data_pos+8])[0]
    audio_data = data[data_pos+8:data_pos+8+min(data_size, 500000)]
    
    # Try all bit positions and byte orders
    for byte_order in ['little', 'big']:
        for bit_pos in range(8):
            bits = []
            
            if byte_order == 'little':
                for i in range(0, len(audio_data), 2):
                    if i+1 < len(audio_data):
                        sample = struct.unpack('<h', audio_data[i:i+2])[0]
                        bits.append((sample >> bit_pos) & 1)
            else:
                for i in range(0, len(audio_data), 2):
                    if i+1 < len(audio_data):
                        sample = struct.unpack('>h', audio_data[i:i+2])[0]
                        bits.append((sample >> bit_pos) & 1)
            
            # Convert to bytes
            extracted = []
            for i in range(0, len(bits) - 8, 8):
                byte_val = 0
                for j in range(8):
                    byte_val = (byte_val << 1) | bits[i + j]
                extracted.append(byte_val)
            
            extracted_data = bytes(extracted)
            
            # Check for flag
            flags = re.findall(rb'Kaal\{[^}]+\}', extracted_data)
            if flags:
                for flag in flags:
                    if flag != b'Kaal{1_th1nk_th15_15_wr0ng}':
                        print(f"\n[+] *** FLAG at bit {bit_pos} ({byte_order}-endian) ***: {flag.decode('utf-8', errors='ignore')}")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
