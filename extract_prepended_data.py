#!/usr/bin/env python3
"""
Extract data that comes BEFORE the MP3 audio starts
Hint: "The challenge starts before the challenge begins"
"""

def find_mp3_start(data):
    """Find where the actual MP3 audio begins"""
    # Look for MP3 frame sync (0xFF 0xFB or 0xFF 0xFA)
    for i in range(len(data) - 1):
        if data[i] == 0xFF and (data[i+1] & 0xE0) == 0xE0:
            return i
    return -1

def analyze_prepended_data():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"[*] Total file size: {len(data)} bytes")
    
    # Find where MP3 actually starts
    mp3_start = find_mp3_start(data)
    print(f"[*] MP3 audio starts at offset: {mp3_start}")
    
    if mp3_start > 0:
        prepended = data[:mp3_start]
        print(f"\n[+] Found {len(prepended)} bytes BEFORE the MP3 audio!")
        print(f"[+] Hex dump of prepended data:")
        print(prepended.hex()[:200])
        
        print(f"\n[+] Raw bytes:")
        print(prepended[:500])
        
        print(f"\n[+] Attempting to decode as text:")
        try:
            text = prepended.decode('utf-8', errors='ignore')
            print(text)
        except:
            pass
        
        try:
            text = prepended.decode('latin-1', errors='ignore')
            print("\n[+] As Latin-1:")
            print(text)
        except:
            pass
        
        # Check for hidden flag in prepended data
        if b'Kaal{' in prepended:
            flag_start = prepended.find(b'Kaal{')
            flag_end = prepended.find(b'}', flag_start)
            if flag_end > flag_start:
                flag = prepended[flag_start:flag_end+1]
                print(f"\n[!!!] FOUND FLAG IN PREPENDED DATA: {flag.decode('utf-8', errors='ignore')}")
        
        # Hint: "spaces are your friend" - maybe LSB steganography or space-based encoding?
        print(f"\n[*] Analyzing spaces in prepended data...")
        spaces = [i for i, b in enumerate(prepended) if b == 0x20]
        print(f"    Found {len(spaces)} space characters")
        if spaces:
            print(f"    Space positions: {spaces}")
        
        # Save prepended data to file for further analysis
        with open('prepended_data.bin', 'wb') as f:
            f.write(prepended)
        print(f"\n[+] Saved prepended data to 'prepended_data.bin'")
    else:
        print("[!] No prepended data found")

if __name__ == "__main__":
    analyze_prepended_data()
