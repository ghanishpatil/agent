#!/usr/bin/env python3
"""
Extract LSB steganography from audio data
The spaces might mark positions in the audio where LSB contains flag bits
"""

def extract_audio_lsb():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find "data" chunk
    data_pos = data.find(b'data')
    if data_pos == -1:
        print("[!] No data chunk found")
        return
    
    print(f"[*] Found 'data' chunk at position {data_pos}")
    
    # Read data chunk size (next 4 bytes after 'data')
    import struct
    chunk_size = struct.unpack('<I', data[data_pos+4:data_pos+8])[0]
    print(f"[*] Data chunk size: {chunk_size} bytes")
    
    # Audio data starts at data_pos + 8
    audio_start = data_pos + 8
    audio_data = data[audio_start:audio_start+chunk_size]
    
    print(f"[*] Audio data length: {len(audio_data)} bytes")
    
    # Find space positions
    space_positions = [i for i, b in enumerate(data) if b == 0x20]
    print(f"[*] Total spaces: {len(space_positions)}")
    
    # Extract LSB from audio samples at space positions
    print("\n[*] Extracting LSB from audio data at space positions:")
    
    lsb_bits = []
    for space_pos in space_positions:
        # If space is within audio data range
        if audio_start <= space_pos < audio_start + len(audio_data):
            # Get the audio sample at this position
            byte_val = data[space_pos]
            lsb = byte_val & 1
            lsb_bits.append(str(lsb))
    
    if len(lsb_bits) > 0:
        binary_str = ''.join(lsb_bits)
        print(f"    Extracted {len(lsb_bits)} LSB bits from spaces in audio")
        decode_binary(binary_str, "LSB from spaces in audio")
    
    # Try extracting LSB from ALL audio samples
    print("\n[*] Extracting LSB from all audio samples:")
    lsb_bits = []
    for i in range(0, min(len(audio_data), 100000)):  # First 100KB
        lsb = audio_data[i] & 1
        lsb_bits.append(str(lsb))
    
    binary_str = ''.join(lsb_bits)
    decode_binary(binary_str, "LSB from all audio samples")
    
    # Try extracting from specific intervals
    print("\n[*] Extracting LSB from audio at space-interval positions:")
    # Use the gaps between spaces as intervals
    gaps = []
    for i in range(1, min(100, len(space_positions))):
        gap = space_positions[i] - space_positions[i-1]
        gaps.append(gap)
    
    # Most common gap is 64
    if gaps:
        common_gap = 64
        lsb_bits = []
        pos = audio_start
        while pos < audio_start + min(len(audio_data), 100000):
            if pos < len(data):
                lsb = data[pos] & 1
                lsb_bits.append(str(lsb))
            pos += common_gap
        
        binary_str = ''.join(lsb_bits)
        decode_binary(binary_str, f"LSB every {common_gap} bytes")

def decode_binary(binary_str, method_name):
    """Try to decode binary string as ASCII"""
    if len(binary_str) < 8:
        return
    
    # Decode as 8-bit ASCII
    chars = []
    for i in range(0, len(binary_str) - 7, 8):
        byte_str = binary_str[i:i+8]
        try:
            char_code = int(byte_str, 2)
            if 32 <= char_code < 127:
                chars.append(chr(char_code))
            else:
                chars.append('.')
        except:
            chars.append('.')
    
    text = ''.join(chars)
    print(f"    {method_name} - First 200 chars: {text[:200]}")
    
    if 'Kaal{' in text:
        start = text.index('Kaal{')
        end = text.index('}', start) + 1
        print(f"\n[!!!] {method_name} FOUND FLAG: {text[start:end]}")
        return True
    
    if 'Kaal' in text or 'kaal' in text.lower():
        idx = text.lower().index('kaal')
        print(f"    Found 'Kaal' near: {text[max(0,idx-10):idx+50]}")
    
    return False

if __name__ == "__main__":
    extract_audio_lsb()
