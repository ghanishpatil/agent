#!/usr/bin/env python3
"""
Find and analyze the real data chunk in the RIFX file
"""

import struct
import re

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

print("[*] Searching for 'data' chunk marker...")

# Find all occurrences of 'data'
data_positions = []
pos = 0
while True:
    pos = data.find(b'data', pos)
    if pos == -1:
        break
    data_positions.append(pos)
    pos += 1

print(f"[+] Found {len(data_positions)} 'data' occurrences at: {data_positions}")

# Analyze each one
for i, pos in enumerate(data_positions):
    print(f"\n[*] Analyzing 'data' at position {pos}:")
    
    # Check if this looks like a chunk header
    if pos + 8 <= len(data):
        # Try little-endian first
        size_le = struct.unpack('<I', data[pos+4:pos+8])[0]
        # Try big-endian
        size_be = struct.unpack('>I', data[pos+4:pos+8])[0]
        
        print(f"    Size (little-endian): {size_le} bytes")
        print(f"    Size (big-endian): {size_be} bytes")
        
        # The file is RIFX (big-endian), so use big-endian
        chunk_size = size_be
        
        if chunk_size < len(data) - pos - 8:
            print(f"    [+] Valid chunk size!")
            
            # Extract the audio data
            audio_data = data[pos+8:pos+8+chunk_size]
            print(f"    Audio data size: {len(audio_data)} bytes")
            print(f"    First 100 bytes: {audio_data[:100]}")
            
            # Check for flag directly in audio data
            flag_match = re.search(rb'Kaal\{[^}]+\}', audio_data)
            if flag_match:
                print(f"    [+] FLAG IN AUDIO DATA: {flag_match.group().decode('utf-8', errors='ignore')}")
            
            # Extract LSB
            print(f"\n    [*] Extracting LSB from audio data...")
            lsb_bits = []
            
            # Try different bit extraction methods
            for method_name, extract_func in [
                ("LSB of each byte", lambda b: b & 1),
                ("2nd bit of each byte", lambda b: (b >> 1) & 1),
                ("MSB of each byte", lambda b: (b >> 7) & 1),
            ]:
                lsb_bits = []
                for byte in audio_data[:100000]:  # First 100KB
                    lsb_bits.append(extract_func(byte))
                
                # Convert to bytes
                lsb_bytes = []
                for j in range(0, len(lsb_bits) - 8, 8):
                    byte_val = 0
                    for k in range(8):
                        byte_val = (byte_val << 1) | lsb_bits[j + k]
                    lsb_bytes.append(byte_val)
                
                lsb_data = bytes(lsb_bytes)
                
                # Search for flag
                flag_in_lsb = re.search(rb'Kaal\{[^}]+\}', lsb_data)
                if flag_in_lsb:
                    print(f"    [+] FLAG FOUND using {method_name}: {flag_in_lsb.group().decode('utf-8', errors='ignore')}")
                
                # Look for readable strings
                lsb_strings = re.findall(rb'[\x20-\x7e]{15,}', lsb_data)
                if lsb_strings:
                    print(f"    Readable strings using {method_name}:")
                    for s in lsb_strings[:10]:
                        decoded = s.decode('utf-8', errors='ignore')
                        if len(decoded) > 10:
                            print(f"        {decoded}")
                            if 'kaal' in decoded.lower():
                                print(f"        ^^^ CONTAINS KAAL!")
            
            # Try extracting from 16-bit samples (WAV is usually 16-bit)
            print(f"\n    [*] Trying 16-bit sample LSB extraction...")
            if len(audio_data) >= 2:
                lsb_bits = []
                for i in range(0, len(audio_data) - 1, 2):
                    # Read as 16-bit big-endian sample
                    sample = struct.unpack('>h', audio_data[i:i+2])[0]
                    lsb_bits.append(sample & 1)
                
                # Convert to bytes
                lsb_bytes = []
                for j in range(0, len(lsb_bits) - 8, 8):
                    byte_val = 0
                    for k in range(8):
                        byte_val = (byte_val << 1) | lsb_bits[j + k]
                    lsb_bytes.append(byte_val)
                
                lsb_data = bytes(lsb_bytes)
                
                # Search for flag
                flag_in_lsb = re.search(rb'Kaal\{[^}]+\}', lsb_data)
                if flag_in_lsb:
                    print(f"    [+] FLAG IN 16-BIT LSB: {flag_in_lsb.group().decode('utf-8', errors='ignore')}")
                
                # Look for strings
                lsb_strings = re.findall(rb'[\x20-\x7e]{15,}', lsb_data)
                if lsb_strings:
                    print(f"    Readable strings in 16-bit LSB:")
                    for s in lsb_strings[:10]:
                        decoded = s.decode('utf-8', errors='ignore')
                        if len(decoded) > 10:
                            print(f"        {decoded}")

print("\n[*] Analysis complete!")
