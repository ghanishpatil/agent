#!/usr/bin/env python3
"""
Properly analyze the RIFX (big-endian WAV) file
"""

import struct
import re

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

print("[*] File analysis:")
print(f"    Total size: {len(data)} bytes")
print(f"    First 16 bytes: {data[:16].hex()}")
print(f"    First 16 bytes (ASCII): {data[:16]}")

# This is RIFX format (big-endian RIFF)
if data[:4] == b'RIFX':
    print("\n[+] This is a RIFX (big-endian WAV) file!")
    
    # Read size (big-endian)
    size = struct.unpack('>I', data[4:8])[0]
    print(f"    Declared size: {size} bytes")
    print(f"    Actual size: {len(data)} bytes")
    
    # Check WAVE marker
    if data[8:12] == b'WAVE':
        print("    Format: WAVE")
    
    # Parse chunks
    print("\n[*] Parsing WAVE chunks...")
    pos = 12
    
    while pos < len(data) - 8:
        chunk_id = data[pos:pos+4]
        if len(chunk_id) < 4 or not all(32 <= b < 127 for b in chunk_id):
            print(f"    Invalid chunk ID at {pos}, stopping")
            break
        
        chunk_size = struct.unpack('>I', data[pos+4:pos+8])[0]
        
        print(f"\n    Chunk '{chunk_id.decode('ascii', errors='ignore')}' at offset {pos}:")
        print(f"        Size: {chunk_size} bytes")
        
        if chunk_size > len(data) - pos - 8:
            print(f"        WARNING: Chunk size exceeds file! Adjusting to {len(data) - pos - 8}")
            chunk_size = len(data) - pos - 8
        
        chunk_data = data[pos+8:pos+8+chunk_size]
        
        # Show preview
        if chunk_size < 200:
            print(f"        Data: {chunk_data[:100]}")
        else:
            print(f"        Data preview: {chunk_data[:100]}")
        
        # Check for flag in this chunk
        flag_match = re.search(rb'Kaal\{[^}]+\}', chunk_data)
        if flag_match:
            print(f"        [+] FLAG FOUND: {flag_match.group().decode('utf-8', errors='ignore')}")
        
        # Special handling for different chunks
        if chunk_id == b'fmt ':
            print(f"        Format chunk details:")
            if len(chunk_data) >= 16:
                audio_format = struct.unpack('>H', chunk_data[0:2])[0]
                num_channels = struct.unpack('>H', chunk_data[2:4])[0]
                sample_rate = struct.unpack('>I', chunk_data[4:8])[0]
                byte_rate = struct.unpack('>I', chunk_data[8:12])[0]
                block_align = struct.unpack('>H', chunk_data[12:14])[0]
                bits_per_sample = struct.unpack('>H', chunk_data[14:16])[0]
                
                print(f"            Audio format: {audio_format}")
                print(f"            Channels: {num_channels}")
                print(f"            Sample rate: {sample_rate} Hz")
                print(f"            Byte rate: {byte_rate}")
                print(f"            Block align: {block_align}")
                print(f"            Bits per sample: {bits_per_sample}")
        
        elif chunk_id == b'data':
            print(f"        Audio data chunk - analyzing for steganography...")
            
            # Extract LSB from audio data
            lsb_bits = []
            sample_count = min(50000, len(chunk_data))
            
            for i in range(sample_count):
                lsb_bits.append(chunk_data[i] & 1)
            
            # Convert bits to bytes
            lsb_bytes = []
            for i in range(0, len(lsb_bits) - 8, 8):
                byte_val = 0
                for j in range(8):
                    byte_val = (byte_val << 1) | lsb_bits[i + j]
                lsb_bytes.append(byte_val)
            
            lsb_data = bytes(lsb_bytes)
            
            # Search for flag
            flag_in_lsb = re.search(rb'Kaal\{[^}]+\}', lsb_data)
            if flag_in_lsb:
                print(f"        [+] FLAG IN LSB: {flag_in_lsb.group().decode('utf-8', errors='ignore')}")
            
            # Look for readable strings
            lsb_strings = re.findall(rb'[\x20-\x7e]{10,}', lsb_data)
            if lsb_strings:
                print(f"        Readable strings in LSB:")
                for s in lsb_strings[:15]:
                    decoded = s.decode('utf-8', errors='ignore')
                    print(f"            {decoded}")
                    if 'kaal' in decoded.lower() or 'flag' in decoded.lower():
                        print(f"            ^^^ INTERESTING!")
        
        # Move to next chunk (word-aligned)
        pos += 8 + chunk_size
        if chunk_size % 2:
            pos += 1
        
        # Safety check
        if pos > len(data):
            break

print("\n[*] Analysis complete!")
