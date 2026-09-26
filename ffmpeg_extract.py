#!/usr/bin/env python3
"""
Use ffmpeg to properly extract and analyze the audio
"""

import subprocess
import os
import re

mp3_file = "chall_media/chall_media.mp3"

print("[*] Using ffmpeg to analyze and extract...")

# 1. Get detailed info
print("\n[1] Getting file info with ffprobe...")
try:
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_format', '-show_streams', mp3_file],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
    # Look for metadata
    if 'comment' in result.stdout.lower() or 'title' in result.stdout.lower():
        print("\n[+] Metadata found - checking for flag...")
        flags = re.findall(r'Kaal\{[^}]+\}', result.stdout)
        if flags:
            for flag in flags:
                print(f"    [+] FLAG IN METADATA: {flag}")
                
except FileNotFoundError:
    print("[-] ffprobe not available")

# 2. Extract cover art if any
print("\n[2] Extracting cover art...")
try:
    result = subprocess.run(
        ['ffmpeg', '-i', mp3_file, '-an', '-vcodec', 'copy', 'cover.jpg', '-y'],
        capture_output=True,
        text=True
    )
    
    if os.path.exists('cover.jpg') and os.path.getsize('cover.jpg') > 0:
        print("[+] Cover art extracted to cover.jpg")
        
        # Check cover art for steganography
        try:
            from stegano import lsb
            secret = lsb.reveal('cover.jpg')
            if secret:
                print(f"[+] Hidden message in cover art:")
                print(secret)
                
                flags = re.findall(r'Kaal\{[^}]+\}', secret)
                if flags:
                    print(f"\n[+] *** FLAG IN COVER ART ***: {flags[0]}")
        except:
            pass
            
        # Also check with strings
        with open('cover.jpg', 'rb') as f:
            cover_data = f.read()
            flags = re.findall(rb'Kaal\{[^}]+\}', cover_data)
            if flags:
                for flag in flags:
                    print(f"[+] FLAG IN COVER IMAGE: {flag.decode('utf-8', errors='ignore')}")
    else:
        print("[-] No cover art found")
        
except FileNotFoundError:
    print("[-] ffmpeg not available")

# 3. Convert to proper WAV
print("\n[3] Converting to WAV with ffmpeg...")
try:
    result = subprocess.run(
        ['ffmpeg', '-i', mp3_file, '-acodec', 'pcm_s16le', '-ar', '44100', 'proper_audio.wav', '-y'],
        capture_output=True,
        text=True
    )
    
    if os.path.exists('proper_audio.wav'):
        print("[+] Converted to proper_audio.wav")
        
        # Now try LSB on this
        print("    Checking for LSB steganography...")
        
        with open('proper_audio.wav', 'rb') as f:
            wav_data = f.read()
        
        # Find data chunk
        data_pos = wav_data.find(b'data')
        if data_pos != -1:
            import struct
            data_size = struct.unpack('<I', wav_data[data_pos+4:data_pos+8])[0]
            audio_samples = wav_data[data_pos+8:data_pos+8+data_size]
            
            print(f"    Audio data size: {data_size} bytes")
            
            # Extract LSB from each byte
            lsb_bits = [byte & 1 for byte in audio_samples[:200000]]
            
            # Convert to bytes
            lsb_bytes = []
            for i in range(0, len(lsb_bits), 8):
                if i + 7 < len(lsb_bits):
                    byte_val = 0
                    for j in range(8):
                        byte_val = (byte_val << 1) | lsb_bits[i + j]
                    lsb_bytes.append(byte_val)
            
            lsb_data = bytes(lsb_bytes)
            
            # Check for flag
            flags = re.findall(rb'Kaal\{[^}]+\}', lsb_data)
            if flags:
                for flag in flags:
                    if flag != b'Kaal{1_th1nk_th15_15_wr0ng}':
                        print(f"\n[+] *** FLAG IN LSB ***: {flag.decode('utf-8', errors='ignore')}")
            
            # Check for readable text
            readable = re.findall(rb'[\x20-\x7e]{20,}', lsb_data)
            if readable:
                print(f"\n    Readable strings in LSB:")
                for s in readable[:10]:
                    decoded = s.decode('utf-8', errors='ignore')
                    print(f"        {decoded}")
                    if 'kaal' in decoded.lower():
                        print(f"        ^^^ CONTAINS KAAL!")
    
except FileNotFoundError:
    print("[-] ffmpeg not available")

print("\n[*] Analysis complete!")
