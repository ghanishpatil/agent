#!/usr/bin/env python3
"""
Use stegano library to extract hidden data
"""

import os

# First, convert to WAV if needed
wav_file = "corrected_audio.wav"
if not os.path.exists(wav_file):
    print("[*] Creating WAV file...")
    with open('chall_media/chall_media.mp3', 'rb') as f:
        data = f.read()
    corrected = b'RIFF' + data[4:]
    with open(wav_file, 'wb') as f:
        f.write(corrected)

# Try stegano LSB
print("[*] Trying stegano LSB extraction...")

try:
    from stegano import lsb
    
    # Try to reveal hidden message
    try:
        secret = lsb.reveal(wav_file)
        if secret:
            print(f"[+] Hidden message found:")
            print(secret)
            
            import re
            flags = re.findall(r'Kaal\{[^}]+\}', secret)
            if flags:
                print(f"\n[+] *** FLAG FOUND ***: {flags[0]}")
        else:
            print("[-] No hidden message found with LSB")
    except Exception as e:
        print(f"[-] LSB reveal error: {e}")
        
except ImportError:
    print("[-] stegano not available")

# Try with PIL/Pillow on images if any were created
print("\n[*] Checking spectrogram images...")
for img_file in ['spectrogram_full.png', 'spectrogram_high_freq.png']:
    if os.path.exists(img_file):
        print(f"\n    Checking {img_file}...")
        try:
            from stegano import lsb
            secret = lsb.reveal(img_file)
            if secret:
                print(f"    [+] Hidden message in {img_file}:")
                print(f"    {secret}")
        except Exception as e:
            print(f"    No LSB data in {img_file}")

print("\n[*] Done!")
