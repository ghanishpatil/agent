import os
import struct

image_path = r"D:\mission-git-hackss\board.png"

print("="*80)
print("DEEP FORENSICS ANALYSIS")
print("="*80)

# Read entire file
with open(image_path, 'rb') as f:
    data = f.read()

print(f"\nFile size: {len(data)} bytes")

# Check PNG structure
print("\n[PNG CHUNK ANALYSIS]")
if data[:8] != b'\x89PNG\r\n\x1a\n':
    print("WARNING: Invalid PNG signature!")
else:
    print("Valid PNG signature")

pos = 8
chunk_num = 0
while pos < len(data) - 12:
    try:
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8]
        
        try:
            chunk_name = chunk_type.decode('ascii')
        except:
            chunk_name = str(chunk_type)
        
        print(f"\nChunk {chunk_num}: {chunk_name}")
        print(f"  Position: {pos}")
        print(f"  Length: {length}")
        
        # Check for text chunks
        if chunk_name in ['tEXt', 'iTXt', 'zTXt', 'tIME']:
            chunk_data = data[pos+8:pos+8+length]
            print(f"  Data: {chunk_data[:200]}")
        
        # Check for unusual chunk types
        if chunk_name not in ['IHDR', 'IDAT', 'IEND', 'PLTE', 'tRNS', 'gAMA', 'cHRM', 'sRGB', 'iCCP', 'pHYs', 'sBIT', 'tIME', 'tEXt', 'iTXt', 'zTXt']:
            print(f"  UNUSUAL CHUNK TYPE: {chunk_name}")
            chunk_data = data[pos+8:pos+8+min(length, 200)]
            print(f"  Data preview: {chunk_data}")
        
        pos += 12 + length
        chunk_num += 1
        
        if chunk_name == 'IEND':
            print(f"\nIEND chunk at position {pos}")
            print(f"Remaining data after IEND: {len(data) - pos} bytes")
            
            if len(data) - pos > 0:
                print("\n*** DATA APPENDED AFTER PNG! ***")
                appended = data[pos:]
                print(f"Appended data length: {len(appended)}")
                print(f"First 200 bytes: {appended[:200]}")
                
                # Check if it's another file
                if appended[:4] == b'PK\x03\x04':
                    print("  Looks like a ZIP file!")
                elif appended[:2] == b'\xff\xd8':
                    print("  Looks like a JPEG file!")
                elif appended[:8] == b'\x89PNG\r\n\x1a\n':
                    print("  Looks like another PNG file!")
                elif b'KAAL{' in appended:
                    idx = appended.index(b'KAAL{')
                    flag_end = appended.find(b'}', idx)
                    if flag_end != -1:
                        flag = appended[idx:flag_end+1].decode('ascii', errors='ignore')
                        print(f"  *** FOUND FLAG: {flag} ***")
                
                # Save appended data
                with open('appended_data.bin', 'wb') as f:
                    f.write(appended)
                print("  Saved to: appended_data.bin")
            break
    except Exception as e:
        print(f"Error parsing chunk at position {pos}: {e}")
        break

# Check for strings in entire file
print("\n[SEARCHING FOR FLAG PATTERNS]")
flag_patterns = [b'KAAL{', b'FLAG{', b'flag{', b'Kaal{']
for pattern in flag_patterns:
    if pattern in data:
        idx = data.index(pattern)
        flag_end = data.find(b'}', idx)
        if flag_end != -1:
            flag = data[idx:flag_end+1].decode('ascii', errors='ignore')
            print(f"Found at offset {idx}: {flag}")

# Look for base64 encoded data
print("\n[CHECKING FOR BASE64 STRINGS]")
import re
# Look for long base64-like strings
base64_pattern = rb'[A-Za-z0-9+/]{40,}={0,2}'
matches = re.findall(base64_pattern, data)
if matches:
    print(f"Found {len(matches)} potential base64 strings")
    for i, match in enumerate(matches[:5]):  # First 5
        print(f"  {i+1}: {match[:60]}...")
        try:
            import base64
            decoded = base64.b64decode(match)
            if b'KAAL' in decoded or b'FLAG' in decoded:
                print(f"    Decoded contains flag: {decoded}")
        except:
            pass

# Check for XOR patterns
print("\n[CHECKING FOR XOR ENCODED DATA]")
# Common XOR keys
xor_keys = [0x42, 0xFF, 0xAA, 0x55, ord('K'), ord('A'), ord('L')]
for key in xor_keys:
    xored = bytes([b ^ key for b in data[:1000]])
    if b'KAAL{' in xored:
        idx = xored.index(b'KAAL{')
        flag_end = xored.find(b'}', idx)
        if flag_end != -1:
            flag = xored[idx:flag_end+1].decode('ascii', errors='ignore')
            print(f"Found with XOR key {hex(key)}: {flag}")

print("\n" + "="*80)
