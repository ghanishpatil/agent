#!/usr/bin/env python3
"""
Check ALL metadata in ALL files very carefully
Maybe soul and time stones ALSO have ICMT comments or other metadata!
"""

import struct

def parse_all_chunks(filename):
    """Parse every single chunk in the WAV file"""
    print(f"\n{'='*70}")
    print(f"File: {filename}")
    print('='*70)
    
    with open(filename, 'rb') as f:
        # Read RIFF header
        riff = f.read(4)
        if riff != b'RIFF':
            print("Not a RIFF file!")
            return {}
        
        file_size = struct.unpack('<I', f.read(4))[0]
        wave_id = f.read(4)
        
        print(f"RIFF size: {file_size}, type: {wave_id}")
        
        metadata = {}
        
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
                
                print(f"\nChunk: {chunk_id.decode('latin-1', errors='ignore')} (size: {chunk_size})")
                
                if chunk_id == b'LIST':
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
                        
                        print(f"    {sub_id.decode('latin-1', errors='ignore')}: ", end='')
                        
                        # Try to decode as text
                        try:
                            text = sub_data.decode('ascii', errors='ignore').strip('\x00')
                            print(f"{text}")
                            
                            if sub_id == b'ICMT':
                                metadata['comment'] = text
                            elif sub_id == b'INAM':
                                metadata['name'] = text
                        except:
                            print(f"{sub_data[:50]}")
                        
                        pos += 8 + sub_size
                        if sub_size % 2:
                            pos += 1
                
                elif chunk_id in [b'ICMT', b'INAM', b'IART', b'ICOP']:
                    # Direct metadata chunks
                    try:
                        text = chunk_data.decode('ascii', errors='ignore').strip('\x00')
                        print(f"  Content: {text}")
                        metadata[chunk_id.decode('latin-1')] = text
                    except:
                        print(f"  Binary data: {chunk_data[:100]}")
                
                elif chunk_id != b'fmt ' and chunk_id != b'data':
                    # Unknown chunk - might contain hidden data
                    print(f"  Data (first 100 bytes): {chunk_data[:100]}")
                    
                    # Check if it contains numbers
                    try:
                        text = chunk_data.decode('ascii', errors='ignore')
                        if any(c.isdigit() for c in text):
                            print(f"  Contains digits!")
                            # Extract numbers
                            import re
                            numbers = re.findall(r'\d{10,}', text)
                            if numbers:
                                print(f"  Found numbers: {numbers}")
                                metadata['hidden_numbers'] = numbers
                    except:
                        pass
            
            except Exception as e:
                print(f"Error: {e}")
                break
        
        return metadata

# Parse all three files
all_metadata = {}
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    metadata = parse_all_chunks(f'stones_extracted/{stone}.wav')
    all_metadata[stone] = metadata

print("\n" + "="*70)
print("SUMMARY OF ALL METADATA")
print("="*70)

for stone, metadata in all_metadata.items():
    print(f"\n{stone}:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

# Check if we now have THREE sets of data
print("\n" + "="*70)
print("DO WE HAVE THREE SETS OF RSA PARAMETERS?")
print("="*70)

comments = []
for stone, metadata in all_metadata.items():
    if 'comment' in metadata:
        comments.append((stone, metadata['comment']))
        print(f"{stone}: {metadata['comment']}")

if len(comments) == 3:
    print("\n*** WE HAVE THREE COMMENTS! These might be n or c values! ***")
elif len(comments) == 1:
    print(f"\nOnly {len(comments)} comment found. Need to find the other two...")
