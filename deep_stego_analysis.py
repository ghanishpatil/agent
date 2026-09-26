#!/usr/bin/env python3
"""
Deep steganography analysis
"""
from PIL import Image
import re

image_path = "image_sJM6Gg8.jpg"

print("="*60)
print("DEEP STEGANOGRAPHY ANALYSIS")
print("="*60)

# Read raw file data
with open(image_path, 'rb') as f:
    raw_data = f.read()

print(f"\n[1] Searching for 'Kaal{{' in raw data:")
if b'Kaal{' in raw_data:
    pos = raw_data.find(b'Kaal{')
    print(f"    Found at offset: 0x{pos:x}")
    
    # Extract the flag
    end_pos = raw_data.find(b'}', pos)
    if end_pos != -1:
        flag = raw_data[pos:end_pos+1].decode('ascii', errors='ignore')
        print(f"    FLAG: {flag}")
else:
    print("    Not found in raw data")

# Check for hidden data at end of file (after JPEG end marker FFD9)
print(f"\n[2] Checking for data after JPEG end marker:")
jpeg_end = b'\xFF\xD9'
end_pos = raw_data.rfind(jpeg_end)
if end_pos != -1:
    print(f"    JPEG ends at offset: 0x{end_pos:x}")
    after_jpeg = raw_data[end_pos+2:]
    print(f"    Data after JPEG: {len(after_jpeg)} bytes")
    
    if len(after_jpeg) > 0:
        print(f"    First 200 bytes: {after_jpeg[:200]}")
        
        # Try to decode as text
        try:
            text = after_jpeg.decode('ascii', errors='ignore')
            print(f"    As text: {text[:500]}")
            
            if 'Kaal{' in text:
                flag = re.search(r'Kaal\{[^}]+\}', text)
                if flag:
                    print(f"\n[+] FLAG FOUND: {flag.group(0)}")
        except:
            pass

# Check for strings in the file
print(f"\n[3] Searching for readable strings:")
strings = re.findall(rb'[\x20-\x7e]{10,}', raw_data)
print(f"    Found {len(strings)} strings")

for s in strings:
    decoded = s.decode('ascii', errors='ignore')
    if 'kaal' in decoded.lower() or 'flag' in decoded.lower() or 'Kaal{' in decoded:
        print(f"    Interesting: {decoded}")

# Check image metadata/comments
print(f"\n[4] Checking JPEG comments:")
# JPEG comment marker is 0xFFFE
comment_marker = b'\xFF\xFE'
pos = 0
while True:
    pos = raw_data.find(comment_marker, pos)
    if pos == -1:
        break
    
    # Length is next 2 bytes (big endian)
    length = int.from_bytes(raw_data[pos+2:pos+4], 'big')
    comment = raw_data[pos+4:pos+2+length]
    print(f"    Comment at 0x{pos:x}: {comment.decode('ascii', errors='ignore')}")
    
    if b'Kaal{' in comment:
        flag = re.search(rb'Kaal\{[^}]+\}', comment)
        if flag:
            print(f"\n[+] FLAG FOUND IN COMMENT: {flag.group(0).decode()}")
    
    pos += 1

# Check for base64 encoded data
print(f"\n[5] Checking for base64 encoded data:")
import base64
# Look for long alphanumeric strings
b64_pattern = rb'[A-Za-z0-9+/]{40,}={0,2}'
matches = re.findall(b64_pattern, raw_data)
print(f"    Found {len(matches)} potential base64 strings")

for match in matches[:10]:
    try:
        decoded = base64.b64decode(match)
        decoded_str = decoded.decode('ascii', errors='ignore')
        if 'Kaal' in decoded_str or 'flag' in decoded_str.lower():
            print(f"    Decoded: {decoded_str}")
            if 'Kaal{' in decoded_str:
                flag = re.search(r'Kaal\{[^}]+\}', decoded_str)
                if flag:
                    print(f"\n[+] FLAG FOUND: {flag.group(0)}")
    except:
        pass

print("\n" + "="*60)
