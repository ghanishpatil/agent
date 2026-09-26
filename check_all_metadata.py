#!/usr/bin/env python3
"""
Check all possible metadata locations
"""

import struct
import re

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

print("[*] Comprehensive metadata check...")

# Check for LIST/INFO chunks (common in WAV files)
print("\n[1] Checking for LIST/INFO chunks...")
list_pos = data.find(b'LIST')
if list_pos != -1:
    print(f"    Found LIST at {list_pos}")
    list_size = struct.unpack('<I', data[list_pos+4:list_pos+8])[0]
    list_data = data[list_pos+8:list_pos+8+list_size]
    print(f"    LIST data: {list_data[:200]}")
    
    flag_match = re.search(rb'Kaal\{[^}]+\}', list_data)
    if flag_match:
        print(f"    [+] FLAG IN LIST: {flag_match.group().decode('utf-8', errors='ignore')}")

# Check for id3 chunks
print("\n[2] Checking for id3 chunks...")
id3_pos = data.find(b'id3 ')
if id3_pos != -1:
    print(f"    Found id3 at {id3_pos}")
    id3_size = struct.unpack('<I', data[id3_pos+4:id3_pos+8])[0]
    id3_data = data[id3_pos+8:id3_pos+8+id3_size]
    print(f"    id3 data: {id3_data[:200]}")
    
    flag_match = re.search(rb'Kaal\{[^}]+\}', id3_data)
    if flag_match:
        print(f"    [+] FLAG IN id3: {flag_match.group().decode('utf-8', errors='ignore')}")

# Check for JUNK chunks (sometimes used to hide data)
print("\n[3] Checking for JUNK chunks...")
junk_pos = data.find(b'JUNK')
if junk_pos != -1:
    print(f"    Found JUNK at {junk_pos}")
    junk_size = struct.unpack('<I', data[junk_pos+4:junk_pos+8])[0]
    junk_data = data[junk_pos+8:junk_pos+8+junk_size]
    print(f"    JUNK data: {junk_data[:200]}")
    
    flag_match = re.search(rb'Kaal\{[^}]+\}', junk_data)
    if flag_match:
        print(f"    [+] FLAG IN JUNK: {flag_match.group().decode('utf-8', errors='ignore')}")

# Check for any custom chunks
print("\n[4] Listing all chunks in file...")
pos = 12  # After RIFF header
chunks_found = []

while pos < len(data) - 8:
    chunk_id = data[pos:pos+4]
    
    # Check if it's a valid chunk ID (printable ASCII)
    if not all(32 <= b < 127 for b in chunk_id):
        pos += 1
        continue
    
    try:
        chunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
    except:
        pos += 1
        continue
    
    if chunk_size > len(data) or chunk_size < 0:
        pos += 1
        continue
    
    chunk_name = chunk_id.decode('ascii', errors='ignore')
    chunks_found.append((chunk_name, pos, chunk_size))
    
    # Check this chunk for flag
    if chunk_size < 1000000:  # Only check reasonable sizes
        chunk_data = data[pos+8:pos+8+min(chunk_size, len(data)-pos-8)]
        flag_match = re.search(rb'Kaal\{[^}]+\}', chunk_data)
        if flag_match and flag_match.group() != b'Kaal{1_th1nk_th15_15_wr0ng}':
            print(f"    [+] DIFFERENT FLAG IN '{chunk_name}': {flag_match.group().decode('utf-8', errors='ignore')}")
    
    pos += 8 + chunk_size
    if chunk_size % 2:  # Word alignment
        pos += 1
    
    if pos > 10000:  # Safety limit for chunk scanning
        break

print(f"\n    Chunks found: {[c[0] for c in chunks_found]}")

# Check for hidden data between chunks
print("\n[5] Checking for data between chunks...")
for i in range(len(chunks_found) - 1):
    chunk1_name, chunk1_pos, chunk1_size = chunks_found[i]
    chunk2_name, chunk2_pos, chunk2_size = chunks_found[i+1]
    
    chunk1_end = chunk1_pos + 8 + chunk1_size
    if chunk1_size % 2:
        chunk1_end += 1
    
    gap = chunk2_pos - chunk1_end
    if gap > 10:
        print(f"    Gap of {gap} bytes between '{chunk1_name}' and '{chunk2_name}'")
        gap_data = data[chunk1_end:chunk2_pos]
        print(f"        Data: {gap_data}")
        
        flag_match = re.search(rb'Kaal\{[^}]+\}', gap_data)
        if flag_match:
            print(f"        [+] FLAG IN GAP: {flag_match.group().decode('utf-8', errors='ignore')}")

# Final check - maybe the flag is just the leet-speak version
print("\n[6] Trying leet-speak variations...")
fake_flag_content = "1_th1nk_th15_15_wr0ng"

# Decode leet speak
leet_decoded = fake_flag_content.replace('1', 'i').replace('3', 'e').replace('5', 's').replace('0', 'o')
print(f"    Leet decoded: {leet_decoded}")
print(f"    Flag: Kaal{{{leet_decoded}}}")

# Try opposite
opposite = leet_decoded.replace('wrong', 'right').replace('think', 'know')
print(f"    Opposite: {opposite}")
print(f"    Flag: Kaal{{{opposite}}}")

# Try with leet speak
opposite_leet = opposite.replace('i', '1').replace('e', '3').replace('s', '5').replace('o', '0')
print(f"    Opposite (leet): {opposite_leet}")
print(f"    Flag: Kaal{{{opposite_leet}}}")

print("\n[*] Analysis complete!")
print("\n[*] MOST LIKELY FLAGS TO TRY:")
print(f"    1. Kaal{{{opposite}}}")
print(f"    2. Kaal{{{opposite_leet}}}")
print(f"    3. Kaal{{i_know_this_is_right}}")
print(f"    4. Kaal{{1_kn0w_th15_15_r1ght}}")
