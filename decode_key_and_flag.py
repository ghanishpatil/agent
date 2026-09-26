#!/usr/bin/env python3
"""
Decode the KEY found at the end of the file
"""

import base64

def decode_key():
    # The key found at the end
    key_b64 = "V1JPTkdLRVk="
    
    print(f"[*] Base64 key: {key_b64}")
    
    # Decode from base64
    key = base64.b64decode(key_b64)
    print(f"[*] Decoded key: {key}")
    print(f"[*] As text: {key.decode('utf-8')}")
    
    # Now let's use this key to decode something
    # Maybe XOR the decoy flag with this key?
    
    decoy = b'Kaal{1_th1nk_th15_15_wr0ng}'
    
    print(f"\n[*] Trying to XOR decoy with key:")
    
    # XOR decoy with key
    result = []
    for i, byte in enumerate(decoy):
        key_byte = key[i % len(key)]
        result.append(byte ^ key_byte)
    
    xored = bytes(result)
    print(f"    XORed result: {xored}")
    print(f"    As text: {xored.decode('latin-1', errors='ignore')}")
    
    # Maybe the key is used to decode the gaps or spaces?
    # Or maybe we need to look for another hidden message?
    
    # Let's also check if there's more data near the KEY
    filepath = r".\chall_media_extracted\chall_media.mp3"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find the KEY position
    key_pos = data.find(b'KEY____________:')
    if key_pos != -1:
        print(f"\n[*] KEY found at position: {key_pos}")
        print(f"[*] Context around KEY:")
        context = data[key_pos-100:key_pos+100]
        print(f"    {context}")
        
        # Check what comes after the key
        after_key = data[key_pos+len(b'KEY____________:V1JPTkdLRVk='):key_pos+200]
        print(f"\n[*] Data after KEY:")
        print(f"    Hex: {after_key.hex()}")
        print(f"    Text: {after_key.decode('latin-1', errors='ignore')}")

if __name__ == "__main__":
    decode_key()
