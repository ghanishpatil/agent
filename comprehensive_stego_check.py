#!/usr/bin/env python3
"""
Comprehensive steganography check
Try multiple methods to find the hidden flag
"""

import struct
import re
import os

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

print("="*60)
print("COMPREHENSIVE STEGANOGRAPHY ANALYSIS")
print("="*60)

# Method 1: Check for appended ZIP/RAR/other archives
print("\n[1] Checking for appended archives...")
archive_sigs = [
    (b'PK\x03\x04', 'ZIP'),
    (b'Rar!\x1a\x07', 'RAR'),
    (b'\x1f\x8b\x08', 'GZIP'),
    (b'7z\xbc\xaf\x27\x1c', '7Z'),
]

for sig, name in archive_sigs:
    pos = data.find(sig)
    if pos != -1 and pos > 1000:  # Not at the beginning
        print(f"[+] Found {name} signature at offset {pos}")
        
        # Try to extract
        archive_data = data[pos:]
        output_file = f'extracted_archive.{name.lower()}'
        with open(output_file, 'wb') as f:
            f.write(archive_data)
        print(f"    Saved to {output_file}")
        
        # Try to extract if it's a ZIP
        if name == 'ZIP':
            import zipfile
            try:
                with zipfile.ZipFile(output_file, 'r') as zf:
                    print(f"    ZIP contents: {zf.namelist()}")
                    zf.extractall('extracted_zip')
                    
                    # Check extracted files for flag
                    for filename in zf.namelist():
                        extracted_path = os.path.join('extracted_zip', filename)
                        if os.path.isfile(extracted_path):
                            with open(extracted_path, 'rb') as ef:
                                extracted_data = ef.read()
                                flag_match = re.search(rb'Kaal\{[^}]+\}', extracted_data)
                                if flag_match:
                                    print(f"    [+] FLAG IN {filename}: {flag_match.group().decode('utf-8', errors='ignore')}")
            except Exception as e:
                print(f"    Could not extract ZIP: {e}")

# Method 2: Check for null-byte separated data
print("\n[2] Checking for null-byte separated hidden data...")
null_sections = data.split(b'\x00' * 10)  # Split on 10+ null bytes
for i, section in enumerate(null_sections):
    if len(section) > 100 and i > 0:  # Skip first section (main file)
        print(f"    Section {i}: {len(section)} bytes")
        flag_match = re.search(rb'Kaal\{[^}]+\}', section)
        if flag_match:
            print(f"    [+] FLAG IN SECTION {i}: {flag_match.group().decode('utf-8', errors='ignore')}")

# Method 3: Check for Base64 encoded data in comments/metadata
print("\n[3] Checking for Base64 encoded data...")
# Look for long Base64 strings
base64_pattern = rb'[A-Za-z0-9+/]{40,}={0,2}'
matches = re.findall(base64_pattern, data)

import base64
for match in matches[:20]:
    try:
        decoded = base64.b64decode(match)
        if len(decoded) > 10:
            # Check if it contains flag
            flag_match = re.search(rb'Kaal\{[^}]+\}', decoded)
            if flag_match:
                print(f"    [+] FLAG IN BASE64: {flag_match.group().decode('utf-8', errors='ignore')}")
                print(f"        Encoded as: {match[:50]}")
    except:
        pass

# Method 4: Check for XOR'd data with common keys
print("\n[4] Checking for XOR'd data...")
common_keys = [b'WRONGKEY', b'RIGHTKEY', b'BHEEM', b'LADDOO', b'KALIA', b'KEY', b'\x00', b'\xff']

for key in common_keys:
    # XOR a portion of the file
    test_data = data[1000:50000]  # Test middle section
    xor_data = bytes([test_data[i] ^ key[i % len(key)] for i in range(len(test_data))])
    
    flag_match = re.search(rb'Kaal\{[^}]+\}', xor_data)
    if flag_match:
        print(f"    [+] FLAG WITH XOR KEY '{key}': {flag_match.group().decode('utf-8', errors='ignore')}")

# Method 5: Check audio data for patterns
print("\n[5] Analyzing audio data patterns...")
data_pos = data.find(b'data')
if data_pos != -1:
    data_size = struct.unpack('<I', data[data_pos+4:data_pos+8])[0]
    audio_data = data[data_pos+8:data_pos+8+data_size]
    
    # Check for repeating patterns that might indicate steganography
    # Look at every Nth byte
    for n in [2, 3, 4, 8, 16]:
        nth_bytes = audio_data[::n][:10000]
        
        # Look for flag
        flag_match = re.search(rb'Kaal\{[^}]+\}', nth_bytes)
        if flag_match:
            print(f"    [+] FLAG IN EVERY {n}TH BYTE: {flag_match.group().decode('utf-8', errors='ignore')}")
        
        # Look for readable text
        text_match = re.findall(rb'[\x20-\x7e]{20,}', nth_bytes)
        if text_match:
            for text in text_match[:5]:
                decoded = text.decode('utf-8', errors='ignore')
                if 'kaal' in decoded.lower() or 'flag' in decoded.lower():
                    print(f"    [+] INTERESTING TEXT IN EVERY {n}TH BYTE: {decoded}")

# Method 6: Check for data in specific bit positions
print("\n[6] Checking specific bit positions...")
data_pos = data.find(b'data')
if data_pos != -1:
    audio_data = data[data_pos+8:data_pos+8+100000]
    
    for bit_pos in range(8):
        bits = []
        for byte in audio_data:
            bits.append((byte >> bit_pos) & 1)
        
        # Convert to bytes
        extracted_bytes = []
        for i in range(0, len(bits) - 8, 8):
            byte_val = 0
            for j in range(8):
                byte_val = (byte_val << 1) | bits[i + j]
            extracted_bytes.append(byte_val)
        
        extracted_data = bytes(extracted_bytes)
        
        flag_match = re.search(rb'Kaal\{[^}]+\}', extracted_data)
        if flag_match:
            print(f"    [+] FLAG IN BIT POSITION {bit_pos}: {flag_match.group().decode('utf-8', errors='ignore')}")

# Method 7: Check the very end of file more carefully
print("\n[7] Detailed analysis of file end...")
tail = data[-5000:]
print(f"    Last 500 bytes (hex): {tail[-500:].hex()}")

# Look for any hidden markers
markers = [b'FLAG', b'flag', b'KEY', b'HIDDEN', b'SECRET', b'REAL']
for marker in markers:
    if marker in tail:
        pos = tail.rfind(marker)
        context = tail[max(0, pos-50):min(len(tail), pos+100)]
        print(f"    Found '{marker.decode()}' at end: {context}")

print("\n" + "="*60)
print("[*] Comprehensive analysis complete!")
print("="*60)
