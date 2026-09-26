#!/usr/bin/env python3
"""
Extract LSB from bytes around spaces
Maybe the flag is hidden in LSB of bytes near spaces
"""

def extract_lsb_steganography():
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find all space positions
    space_positions = []
    for i, byte in enumerate(data):
        if byte == 0x20:  # space character
            space_positions.append(i)
    
    print(f"[*] Found {len(space_positions)} spaces")
    
    # Extract LSB from bytes before each space
    print("\n[*] Extracting LSB from bytes BEFORE spaces:")
    lsb_bits = []
    for pos in space_positions:
        if pos > 0:
            byte_val = data[pos - 1]
            lsb = byte_val & 1
            lsb_bits.append(str(lsb))
    
    binary_str = ''.join(lsb_bits)
    decode_binary(binary_str, "LSB before spaces")
    
    # Extract LSB from bytes after each space
    print("\n[*] Extracting LSB from bytes AFTER spaces:")
    lsb_bits = []
    for pos in space_positions:
        if pos + 1 < len(data):
            byte_val = data[pos + 1]
            lsb = byte_val & 1
            lsb_bits.append(str(lsb))
    
    binary_str = ''.join(lsb_bits)
    decode_binary(binary_str, "LSB after spaces")
    
    # Extract multiple LSBs (2 bits)
    print("\n[*] Extracting 2 LSBs from bytes BEFORE spaces:")
    bits = []
    for pos in space_positions:
        if pos > 0:
            byte_val = data[pos - 1]
            two_bits = byte_val & 0b11
            bits.append(format(two_bits, '02b'))
    
    binary_str = ''.join(bits)
    decode_binary(binary_str, "2 LSBs before spaces")

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
    
    # Also check for partial matches
    if 'Kaal' in text or 'kaal' in text.lower():
        idx = text.lower().index('kaal')
        print(f"    Found 'Kaal' at position {idx}: {text[max(0,idx-10):idx+50]}")
    
    return False

if __name__ == "__main__":
    extract_lsb_steganography()
