#!/usr/bin/env python3
"""Deep analysis of WAV file structure to find RSA params"""

import wave
import struct

def analyze_wav_chunks(filename):
    """Parse all RIFF chunks in WAV file"""
    print(f"\n{'='*60}")
    print(f"Deep analysis: {filename}")
    print('='*60)
    
    with open(filename, 'rb') as f:
        # Read RIFF header
        riff = f.read(4)
        if riff != b'RIFF':
            print("Not a RIFF file!")
            return
        
        file_size = struct.unpack('<I', f.read(4))[0]
        wave_id = f.read(4)
        
        print(f"RIFF file, size: {file_size}, type: {wave_id}")
        
        # Read all chunks
        while f.tell() < file_size + 8:
            try:
                chunk_id = f.read(4)
                if len(chunk_id) < 4:
                    break
                    
                chunk_size = struct.unpack('<I', f.read(4))[0]
                chunk_data = f.read(chunk_size)
                
                # Pad if odd size
                if chunk_size % 2:
                    f.read(1)
                
                print(f"\nChunk: {chunk_id} (size: {chunk_size})")
                
                if chunk_id == b'fmt ':
                    # Format chunk
                    fmt = struct.unpack('<HHIIHH', chunk_data[:16])
                    print(f"  Format: {fmt[0]}, Channels: {fmt[1]}, Sample Rate: {fmt[2]}")
                    print(f"  Byte Rate: {fmt[3]}, Block Align: {fmt[4]}, Bits/Sample: {fmt[5]}")
                
                elif chunk_id == b'LIST':
                    print(f"  LIST data: {chunk_data[:200]}")
                    # Parse LIST subchunks
                    list_type = chunk_data[:4]
                    print(f"  LIST type: {list_type}")
                    
                    pos = 4
                    while pos < len(chunk_data):
                        if pos + 8 > len(chunk_data):
                            break
                        sub_id = chunk_data[pos:pos+4]
                        sub_size = struct.unpack('<I', chunk_data[pos+4:pos+8])[0]
                        sub_data = chunk_data[pos+8:pos+8+sub_size]
                        print(f"    Sub-chunk: {sub_id}, size: {sub_size}")
                        
                        if sub_id == b'ICMT':
                            comment = sub_data.decode('ascii', errors='ignore').strip('\x00')
                            print(f"      Comment: {comment}")
                        elif sub_id == b'INAM':
                            name = sub_data.decode('ascii', errors='ignore').strip('\x00')
                            print(f"      Name: {name}")
                        else:
                            print(f"      Data: {sub_data[:100]}")
                        
                        pos += 8 + sub_size
                        if sub_size % 2:
                            pos += 1
                
                elif chunk_id == b'data':
                    print(f"  Audio data size: {chunk_size}")
                    # Check first few samples
                    samples = struct.unpack(f'<{min(20, chunk_size//2)}h', chunk_data[:40])
                    print(f"  First samples: {samples}")
                
                else:
                    # Unknown chunk - might contain RSA data
                    print(f"  Raw data (first 200 bytes): {chunk_data[:200]}")
                    # Try to decode as text
                    try:
                        text = chunk_data.decode('ascii', errors='ignore')
                        if any(c in text for c in ['n=', 'c=', 'e=']):
                            print(f"  Text content: {text[:500]}")
                    except:
                        pass
            
            except Exception as e:
                print(f"Error reading chunk: {e}")
                break

# Analyze all three files
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    analyze_wav_chunks(f'stones_extracted/{stone}.wav')
