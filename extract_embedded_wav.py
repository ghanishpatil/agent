#!/usr/bin/env python3
"""
Extract embedded WAV file from MP3
"""

import re

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

print("[*] Searching for RIFF/RIFX WAV signatures...")

# Search for RIFF or RIFX (big-endian RIFF)
riff_positions = []
for pattern in [b'RIFF', b'RIFX']:
    pos = 0
    while True:
        pos = data.find(pattern, pos)
        if pos == -1:
            break
        # Check if followed by size and WAVE
        if pos + 12 < len(data):
            if data[pos+8:pos+12] == b'WAVE':
                riff_positions.append(pos)
                print(f"[+] Found {pattern.decode()} WAV at position: {pos}")
        pos += 1

if riff_positions:
    for i, pos in enumerate(riff_positions):
        # Read the size from RIFF header
        size_bytes = data[pos+4:pos+8]
        if data[pos:pos+4] == b'RIFX':
            # Big-endian
            import struct
            size = struct.unpack('>I', size_bytes)[0]
        else:
            # Little-endian
            import struct
            size = struct.unpack('<I', size_bytes)[0]
        
        print(f"[*] WAV file size: {size} bytes")
        
        # Extract the WAV file
        wav_data = data[pos:pos+8+size]
        output_file = f'extracted_audio_{i}.wav'
        
        with open(output_file, 'wb') as f:
            f.write(wav_data)
        
        print(f"[+] Extracted WAV to: {output_file}")
        
        # Analyze the WAV file
        print(f"\n[*] Analyzing {output_file}...")
        
        # Look for flag in WAV data
        flag_match = re.search(rb'Kaal\{[^}]+\}', wav_data)
        if flag_match:
            print(f"[+] FLAG IN WAV: {flag_match.group().decode('utf-8', errors='ignore')}")
        
        # Check for text in WAV
        text_strings = re.findall(rb'[\x20-\x7e]{8,}', wav_data)
        if text_strings:
            print(f"[*] Text strings in WAV:")
            for s in text_strings[:20]:
                decoded = s.decode('utf-8', errors='ignore')
                if 'kaal' in decoded.lower() or 'flag' in decoded.lower() or 'key' in decoded.lower():
                    print(f"    {decoded}")
        
        # Try to read WAV metadata
        print(f"\n[*] Checking WAV chunks...")
        chunk_pos = pos + 12  # After RIFF header
        while chunk_pos < pos + 8 + size - 8:
            chunk_id = data[chunk_pos:chunk_pos+4]
            if len(chunk_id) < 4:
                break
            
            chunk_size_bytes = data[chunk_pos+4:chunk_pos+8]
            if len(chunk_size_bytes) < 4:
                break
            
            import struct
            if data[pos:pos+4] == b'RIFX':
                chunk_size = struct.unpack('>I', chunk_size_bytes)[0]
            else:
                chunk_size = struct.unpack('<I', chunk_size_bytes)[0]
            
            print(f"    Chunk: {chunk_id} (size: {chunk_size})")
            
            # Check for interesting chunks
            if chunk_id in [b'INFO', b'LIST', b'id3 ', b'ID3 ']:
                chunk_data = data[chunk_pos+8:chunk_pos+8+chunk_size]
                print(f"        Data preview: {chunk_data[:100]}")
                
                # Look for flag
                flag_in_chunk = re.search(rb'Kaal\{[^}]+\}', chunk_data)
                if flag_in_chunk:
                    print(f"[+] FLAG IN CHUNK: {flag_in_chunk.group().decode('utf-8', errors='ignore')}")
            
            chunk_pos += 8 + chunk_size
            if chunk_size % 2:  # Chunks are word-aligned
                chunk_pos += 1
        
        # Check LSB of audio samples
        print(f"\n[*] Checking LSB steganography in WAV...")
        
        # Find data chunk
        data_chunk_pos = wav_data.find(b'data')
        if data_chunk_pos != -1:
            import struct
            data_size = struct.unpack('<I', wav_data[data_chunk_pos+4:data_chunk_pos+8])[0]
            audio_samples = wav_data[data_chunk_pos+8:data_chunk_pos+8+data_size]
            
            print(f"    Audio data size: {data_size} bytes")
            
            # Extract LSB
            lsb_bits = []
            for byte in audio_samples[:10000]:  # First 10KB
                lsb_bits.append(byte & 1)
            
            # Convert to bytes
            lsb_bytes = []
            for i in range(0, len(lsb_bits) - 8, 8):
                byte_val = 0
                for j in range(8):
                    byte_val = (byte_val << 1) | lsb_bits[i + j]
                lsb_bytes.append(byte_val)
            
            lsb_data = bytes(lsb_bytes)
            
            # Look for flag
            flag_in_lsb = re.search(rb'Kaal\{[^}]+\}', lsb_data)
            if flag_in_lsb:
                print(f"[+] FLAG IN LSB: {flag_in_lsb.group().decode('utf-8', errors='ignore')}")
            
            # Look for readable text
            lsb_strings = re.findall(rb'[\x20-\x7e]{8,}', lsb_data)
            if lsb_strings:
                print(f"    LSB strings:")
                for s in lsb_strings[:10]:
                    print(f"        {s.decode('utf-8', errors='ignore')}")

else:
    print("[-] No WAV files found")

print("\n[*] Extraction complete!")
