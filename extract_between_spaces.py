#!/usr/bin/env python3
"""
Extract and analyze data BETWEEN spaces
"""

def extract_between_spaces():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find all space positions
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    
    print(f"[*] Total spaces: {len(space_positions)}")
    
    # Extract chunks between spaces
    print(f"\n[*] Analyzing chunks between first 20 spaces:")
    for i in range(min(20, len(space_positions)-1)):
        start = space_positions[i] + 1
        end = space_positions[i+1]
        chunk = data[start:end]
        chunk_len = len(chunk)
        
        # Try to decode as text
        try:
            text = chunk.decode('utf-8', errors='ignore')
            if text.isprintable():
                print(f"Chunk {i}: len={chunk_len}, text='{text[:50]}'")
            else:
                print(f"Chunk {i}: len={chunk_len}, hex={chunk[:20].hex()}")
        except:
            print(f"Chunk {i}: len={chunk_len}, hex={chunk[:20].hex()}")
    
    # Collect all printable text between spaces
    print(f"\n[*] Collecting all printable text between spaces:")
    all_text = []
    for i in range(len(space_positions)-1):
        start = space_positions[i] + 1
        end = space_positions[i+1]
        chunk = data[start:end]
        
        try:
            text = chunk.decode('utf-8', errors='ignore')
            # Only keep printable ASCII
            printable = ''.join(c for c in text if 32 <= ord(c) <= 126)
            if printable:
                all_text.append(printable)
        except:
            pass
    
    combined_text = ''.join(all_text)
    print(f"[*] Combined printable text length: {len(combined_text)}")
    print(f"[*] First 500 characters:")
    print(combined_text[:500])
    
    # Search for flag
    if 'Kaal{' in combined_text:
        start = combined_text.find('Kaal{')
        end = combined_text.find('}', start)
        if end > start:
            print(f"\n[!!!] FOUND FLAG: {combined_text[start:end+1]}")
    else:
        # Print more to search manually
        print(f"\n[*] Full text (searching for flag pattern):")
        print(combined_text)

if __name__ == "__main__":
    extract_between_spaces()
