#!/usr/bin/env python3
"""
Final attempt - try all remaining steganography methods
"""

import struct
import re
import subprocess
import os

# Try using the corrected WAV file
wav_file = "corrected_audio.wav"

if not os.path.exists(wav_file):
    print("[*] Creating corrected WAV file...")
    with open('chall_media/chall_media.mp3', 'rb') as f:
        data = f.read()
    corrected = b'RIFF' + data[4:]
    with open(wav_file, 'wb') as f:
        f.write(corrected)

print("[*] Trying various steganography tools...")

# Try steghide with empty password
print("\n[1] Trying steghide with empty password...")
try:
    result = subprocess.run(
        ['steghide', 'extract', '-sf', wav_file, '-p', '', '-xf', 'steghide_output.txt', '-f'],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print("[+] Steghide extraction successful!")
        if os.path.exists('steghide_output.txt'):
            with open('steghide_output.txt', 'rb') as f:
                extracted = f.read()
            print(f"    Extracted: {extracted}")
            
            flag_match = re.search(rb'Kaal\{[^}]+\}', extracted)
            if flag_match:
                print(f"\n[+] *** REAL FLAG ***: {flag_match.group().decode('utf-8', errors='ignore')}")
    else:
        print(f"    steghide failed: {result.stderr[:200]}")
except FileNotFoundError:
    print("    steghide not installed")
except Exception as e:
    print(f"    Error: {e}")

# Try with common passwords
passwords = ['', 'bheem', 'laddoo', 'kalia', 'password', 'WRONGKEY', 'chhota']
for pwd in passwords:
    try:
        result = subprocess.run(
            ['steghide', 'extract', '-sf', wav_file, '-p', pwd, '-xf', f'out_{pwd}.txt', '-f'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"[+] Success with password: '{pwd}'")
            output_file = f'out_{pwd}.txt'
            if os.path.exists(output_file):
                with open(output_file, 'rb') as f:
                    extracted = f.read()
                print(f"    Extracted: {extracted}")
                
                flag_match = re.search(rb'Kaal\{[^}]+\}', extracted)
                if flag_match:
                    print(f"\n[+] *** REAL FLAG ***: {flag_match.group().decode('utf-8', errors='ignore')}")
                    break
    except:
        pass

# Check for OpenPuff signature
print("\n[2] Checking for OpenPuff signature...")
with open(wav_file, 'rb') as f:
    data = f.read()

# OpenPuff uses specific markers
if b'OpenPuff' in data:
    print("[+] OpenPuff signature found!")

# Check for DeepSound signature
print("\n[3] Checking for DeepSound format...")
# DeepSound encrypted files have specific patterns

# Try manual LSB with different methods
print("\n[4] Trying advanced LSB extraction...")

data_pos = data.find(b'data')
if data_pos != -1:
    data_size = struct.unpack('<I', data[data_pos+4:data_pos+8])[0]
    audio_data = data[data_pos+8:data_pos+8+data_size]
    
    # Method: Extract from low byte of 16-bit samples
    print("    Extracting from low byte of samples...")
    extracted_bytes = []
    for i in range(0, min(len(audio_data), 100000), 2):
        if i+1 < len(audio_data):
            # Get low byte of 16-bit sample
            low_byte = audio_data[i]
            extracted_bytes.append(low_byte)
    
    extracted_data = bytes(extracted_bytes)
    
    # Look for flag
    flag_match = re.search(rb'Kaal\{[^}]+\}', extracted_data)
    if flag_match:
        print(f"    [+] FLAG IN LOW BYTES: {flag_match.group().decode('utf-8', errors='ignore')}")
    
    # Look for readable text
    text_matches = re.findall(rb'[\x20-\x7e]{20,}', extracted_data)
    if text_matches:
        print(f"    Readable text in low bytes:")
        for text in text_matches[:10]:
            decoded = text.decode('utf-8', errors='ignore')
            print(f"        {decoded}")
            if 'kaal' in decoded.lower():
                print(f"        ^^^ CONTAINS KAAL!")

# Try extracting from high byte
print("\n    Extracting from high byte of samples...")
extracted_bytes = []
for i in range(1, min(len(audio_data), 100000), 2):
    extracted_bytes.append(audio_data[i])

extracted_data = bytes(extracted_bytes)

flag_match = re.search(rb'Kaal\{[^}]+\}', extracted_data)
if flag_match:
    print(f"    [+] FLAG IN HIGH BYTES: {flag_match.group().decode('utf-8', errors='ignore')}")

# Look for text
text_matches = re.findall(rb'[\x20-\x7e]{20,}', extracted_data)
if text_matches:
    print(f"    Readable text in high bytes:")
    for text in text_matches[:10]:
        decoded = text.decode('utf-8', errors='ignore')
        print(f"        {decoded}")

# Try zsteg-like analysis (check all bit planes)
print("\n[5] Checking all bit planes and byte positions...")
for byte_offset in [0, 1]:
    for bit_pos in range(8):
        bits = []
        for i in range(byte_offset, min(len(audio_data), 50000), 2):
            byte = audio_data[i]
            bits.append((byte >> bit_pos) & 1)
        
        # Convert to bytes
        extracted_bytes = []
        for j in range(0, len(bits) - 8, 8):
            byte_val = 0
            for k in range(8):
                byte_val = (byte_val << 1) | bits[j + k]
            extracted_bytes.append(byte_val)
        
        extracted_data = bytes(extracted_bytes)
        
        # Check for flag
        flag_match = re.search(rb'Kaal\{[^}]+\}', extracted_data)
        if flag_match:
            print(f"    [+] FLAG at byte_offset={byte_offset}, bit={bit_pos}: {flag_match.group().decode('utf-8', errors='ignore')}")
        
        # Check for readable text with "kaal"
        if b'kaal' in extracted_data.lower() or b'Kaal' in extracted_data:
            text_matches = re.findall(rb'[\x20-\x7e]{15,}', extracted_data)
            if text_matches:
                print(f"    Interesting text at byte_offset={byte_offset}, bit={bit_pos}:")
                for text in text_matches[:5]:
                    decoded = text.decode('utf-8', errors='ignore')
                    if 'kaal' in decoded.lower():
                        print(f"        {decoded}")

print("\n[*] Analysis complete!")
