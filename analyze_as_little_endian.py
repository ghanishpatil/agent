#!/usr/bin/env python3
"""
Analyze the file as little-endian RIFF/WAV
The first 4 bytes spell RIFX but maybe it's actually RIFF with corruption
"""

import struct
import re

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

print("[*] Treating file as little-endian RIFF...")
print(f"    First 4 bytes: {data[:4]} (should be RIFF)")
print(f"    Bytes 8-12: {data[8:12]} (should be WAVE)")

# Parse as little-endian
size = struct.unpack('<I', data[4:8])[0]
print(f"    File size (little-endian): {size} bytes")

# Find fmt chunk
fmt_pos = data.find(b'fmt ')
if fmt_pos != -1:
    print(f"\n[*] Found fmt chunk at {fmt_pos}")
    fmt_size = struct.unpack('<I', data[fmt_pos+4:fmt_pos+8])[0]
    print(f"    fmt size: {fmt_size} bytes")
    
    if fmt_size == 16 or fmt_size == 18:
        fmt_data = data[fmt_pos+8:fmt_pos+8+fmt_size]
        
        audio_format = struct.unpack('<H', fmt_data[0:2])[0]
        num_channels = struct.unpack('<H', fmt_data[2:4])[0]
        sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
        byte_rate = struct.unpack('<I', fmt_data[8:12])[0]
        block_align = struct.unpack('<H', fmt_data[12:14])[0]
        bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
        
        print(f"    Audio format: {audio_format} (1=PCM)")
        print(f"    Channels: {num_channels}")
        print(f"    Sample rate: {sample_rate} Hz")
        print(f"    Byte rate: {byte_rate}")
        print(f"    Block align: {block_align}")
        print(f"    Bits per sample: {bits_per_sample}")

# Find data chunk
data_pos = data.find(b'data')
if data_pos != -1:
    print(f"\n[*] Found data chunk at {data_pos}")
    data_size = struct.unpack('<I', data[data_pos+4:data_pos+8])[0]
    print(f"    Data size: {data_size} bytes")
    
    audio_data = data[data_pos+8:data_pos+8+data_size]
    print(f"    Extracted audio data: {len(audio_data)} bytes")
    
    # Save the audio data
    with open('audio_data_only.bin', 'wb') as f:
        f.write(audio_data)
    print(f"    Saved to audio_data_only.bin")
    
    # Check for flag in raw audio
    flag_match = re.search(rb'Kaal\{[^}]+\}', audio_data)
    if flag_match:
        print(f"\n[+] FLAG IN RAW AUDIO: {flag_match.group().decode('utf-8', errors='ignore')}")
    
    # LSB extraction from 16-bit samples (little-endian)
    print(f"\n[*] Extracting LSB from 16-bit little-endian samples...")
    
    lsb_bits = []
    for i in range(0, min(len(audio_data), 200000) - 1, 2):
        sample = struct.unpack('<h', audio_data[i:i+2])[0]
        lsb_bits.append(sample & 1)
    
    # Convert bits to bytes
    lsb_bytes = []
    for i in range(0, len(lsb_bits) - 8, 8):
        byte_val = 0
        for j in range(8):
            byte_val = (byte_val << 1) | lsb_bits[i + j]
        lsb_bytes.append(byte_val)
    
    lsb_data = bytes(lsb_bytes)
    
    # Save LSB data
    with open('lsb_data.bin', 'wb') as f:
        f.write(lsb_data)
    print(f"    Saved LSB data to lsb_data.bin ({len(lsb_data)} bytes)")
    
    # Search for flag
    flag_in_lsb = re.search(rb'Kaal\{[^}]+\}', lsb_data)
    if flag_in_lsb:
        print(f"\n[+] *** FLAG FOUND IN LSB ***: {flag_in_lsb.group().decode('utf-8', errors='ignore')}")
    
    # Look for readable strings
    lsb_strings = re.findall(rb'[\x20-\x7e]{12,}', lsb_data)
    if lsb_strings:
        print(f"\n[*] Readable strings in LSB data:")
        for s in lsb_strings[:30]:
            decoded = s.decode('utf-8', errors='ignore')
            print(f"    {decoded}")
            if 'kaal' in decoded.lower() or 'flag' in decoded.lower() or 'bheem' in decoded.lower():
                print(f"    ^^^ INTERESTING!")
    
    # Try byte-by-byte LSB too
    print(f"\n[*] Trying byte-by-byte LSB extraction...")
    lsb_bits = [byte & 1 for byte in audio_data[:200000]]
    
    lsb_bytes = []
    for i in range(0, len(lsb_bits) - 8, 8):
        byte_val = 0
        for j in range(8):
            byte_val = (byte_val << 1) | lsb_bits[i + j]
        lsb_bytes.append(byte_val)
    
    lsb_data_byte = bytes(lsb_bytes)
    
    flag_in_lsb_byte = re.search(rb'Kaal\{[^}]+\}', lsb_data_byte)
    if flag_in_lsb_byte:
        print(f"\n[+] *** FLAG IN BYTE LSB ***: {flag_in_lsb_byte.group().decode('utf-8', errors='ignore')}")
    
    # Look for strings
    lsb_strings_byte = re.findall(rb'[\x20-\x7e]{12,}', lsb_data_byte)
    if lsb_strings_byte:
        print(f"\n[*] Readable strings in byte LSB:")
        for s in lsb_strings_byte[:30]:
            decoded = s.decode('utf-8', errors='ignore')
            print(f"    {decoded}")

print("\n[*] Analysis complete!")
