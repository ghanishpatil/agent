#!/usr/bin/env python3
"""
Analyze RIFX/WAVE file structure
Look for hidden data in chunks
"""

import struct

def analyze_wave_structure():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"[*] File size: {len(data)} bytes")
    
    # Parse RIFX header
    if data[:4] != b'RIFX':
        print("[!] Not a RIFX file!")
        return
    
    print("[*] RIFX header found")
    
    # Read file size from header (big-endian for RIFX)
    file_size = struct.unpack('>I', data[4:8])[0]
    print(f"[*] RIFX file size field: {file_size} bytes")
    
    # Check WAVE format
    if data[8:12] != b'WAVE':
        print("[!] Not a WAVE file!")
        return
    
    print("[*] WAVE format confirmed")
    
    # Parse chunks
    pos = 12
    chunks = []
    
    while pos < len(data) - 8:
        chunk_id = data[pos:pos+4]
        chunk_size = struct.unpack('>I', data[pos+4:pos+8])[0]  # Big-endian for RIFX
        
        print(f"\n[*] Chunk at offset {pos}:")
        print(f"    ID: {chunk_id}")
        print(f"    Size: {chunk_size} bytes")
        
        chunks.append({
            'id': chunk_id,
            'offset': pos,
            'size': chunk_size,
            'data_offset': pos + 8
        })
        
        # Check for suspicious chunks or hidden data
        if chunk_id == b'fmt ':
            print(f"    Format chunk - analyzing...")
            fmt_data = data[pos+8:pos+8+chunk_size]
            if len(fmt_data) >= 16:
                audio_format = struct.unpack('<H', fmt_data[0:2])[0]
                num_channels = struct.unpack('<H', fmt_data[2:4])[0]
                sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                print(f"    Audio format: {audio_format}")
                print(f"    Channels: {num_channels}")
                print(f"    Sample rate: {sample_rate}")
        
        elif chunk_id == b'data':
            print(f"    Data chunk - contains audio samples")
            # Check first few bytes of data
            sample_data = data[pos+8:pos+8+min(100, chunk_size)]
            print(f"    First 100 bytes (hex): {sample_data.hex()[:200]}")
        
        elif chunk_id not in [b'fmt ', b'data', b'LIST', b'INFO']:
            print(f"    [!] UNUSUAL CHUNK: {chunk_id}")
            chunk_data = data[pos+8:pos+8+min(200, chunk_size)]
            print(f"    First bytes (hex): {chunk_data.hex()}")
            print(f"    As text: {chunk_data.decode('latin-1', errors='ignore')}")
            
            # Check for flag
            if b'Kaal{' in data[pos+8:pos+8+chunk_size]:
                flag_data = data[pos+8:pos+8+chunk_size]
                text = flag_data.decode('latin-1', errors='ignore')
                start = text.index('Kaal{')
                end = text.index('}', start) + 1
                print(f"\n[!!!] FOUND FLAG IN CHUNK: {text[start:end]}")
                return
        
        # Move to next chunk (add padding if odd size)
        pos += 8 + chunk_size
        if chunk_size % 2 == 1:
            pos += 1
    
    print(f"\n[*] Total chunks found: {len(chunks)}")
    
    # Check for data after all chunks
    if pos < len(data):
        print(f"\n[*] Extra data after chunks: {len(data) - pos} bytes")
        extra_data = data[pos:pos+200]
        print(f"    First 200 bytes (hex): {extra_data.hex()}")
        print(f"    As text: {extra_data.decode('latin-1', errors='ignore')}")
        
        # Check for flag in extra data
        if b'Kaal{' in data[pos:]:
            text = data[pos:].decode('latin-1', errors='ignore')
            start = text.index('Kaal{')
            end = text.index('}', start) + 1
            print(f"\n[!!!] FOUND FLAG IN EXTRA DATA: {text[start:end]}")

if __name__ == "__main__":
    analyze_wave_structure()
