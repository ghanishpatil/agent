#!/usr/bin/env python3
"""
Decode flag from space positions
Hint: "spaces are your friend"
"""

def analyze_space_encoding():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find all space (0x20) positions
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    
    print(f"[*] Total spaces found: {len(space_positions)}")
    print(f"[*] First 50 space positions: {space_positions[:50]}")
    
    # Analyze the gaps between spaces
    if len(space_positions) > 1:
        gaps = [space_positions[i+1] - space_positions[i] for i in range(len(space_positions)-1)]
        print(f"\n[*] First 50 gaps between spaces: {gaps[:50]}")
        
        # Check if gaps represent ASCII values
        print(f"\n[*] Attempting to decode gaps as ASCII characters:")
        try:
            flag_chars = []
            for gap in gaps:
                if 32 <= gap <= 126:  # Printable ASCII range
                    flag_chars.append(chr(gap))
                else:
                    flag_chars.append(f"[{gap}]")
            
            flag_text = ''.join(flag_chars)
            print(flag_text[:500])
            
            # Look for Kaal{ pattern
            if 'Kaal{' in flag_text:
                start = flag_text.find('Kaal{')
                end = flag_text.find('}', start)
                if end > start:
                    print(f"\n[!!!] FOUND FLAG: {flag_text[start:end+1]}")
        except Exception as e:
            print(f"Error decoding: {e}")
    
    # Try extracting bytes at space positions
    print(f"\n[*] Bytes at space positions:")
    bytes_at_spaces = [data[pos] if pos < len(data) else 0 for pos in space_positions[:100]]
    print(bytes_at_spaces[:50])
    
    # Try extracting bytes AFTER spaces
    print(f"\n[*] Bytes immediately AFTER space positions:")
    bytes_after_spaces = [data[pos+1] if pos+1 < len(data) else 0 for pos in space_positions[:200]]
    print(bytes_after_spaces[:50])
    
    # Try to decode as ASCII
    try:
        text_after = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in bytes_after_spaces])
        print(f"As text: {text_after}")
        
        if 'Kaal{' in text_after:
            start = text_after.find('Kaal{')
            end = text_after.find('}', start)
            if end > start:
                print(f"\n[!!!] FOUND FLAG: {text_after[start:end+1]}")
    except:
        pass

if __name__ == "__main__":
    analyze_space_encoding()
