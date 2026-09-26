#!/usr/bin/env python3
"""
Deep audio steganography analysis for chall_media.mp3
Looking for the REAL flag hidden in the audio data
"""

import os
import struct
import binascii

def extract_lsb_from_audio(filepath):
    """Extract LSB from audio data"""
    print("[*] Extracting LSB from audio frames...")
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Skip ID3 tags if present
    offset = 0
    if data[:3] == b'ID3':
        version = data[3:5]
        size_bytes = data[6:10]
        tag_size = (size_bytes[0] << 21) | (size_bytes[1] << 14) | (size_bytes[2] << 7) | size_bytes[3]
        offset = 10 + tag_size
        print(f"[*] Skipping ID3 tag: {tag_size} bytes")
    
    # Find MP3 frame data
    mp3_data = data[offset:]
    
    # Extract LSB from bytes
    lsb_bits = []
    for byte in mp3_data[:100000]:  # Check first 100KB
        lsb_bits.append(byte & 1)
    
    # Convert bits to bytes
    lsb_bytes = []
    for i in range(0, len(lsb_bits) - 8, 8):
        byte_val = 0
        for j in range(8):
            byte_val = (byte_val << 1) | lsb_bits[i + j]
        lsb_bytes.append(byte_val)
    
    lsb_data = bytes(lsb_bytes)
    
    # Search for flag pattern
    import re
    flags = re.findall(b'Kaal\\{[^}]+\\}', lsb_data)
    if flags:
        print("[+] FLAG FOUND IN LSB:")
        for flag in flags:
            print(f"    {flag.decode('utf-8', errors='ignore')}")
    
    # Save LSB data
    with open('lsb_extracted.bin', 'wb') as f:
        f.write(lsb_data[:10000])
    print("[*] Saved LSB data to lsb_extracted.bin")
    
    # Check for readable strings
    strings = re.findall(b'[\x20-\x7e]{8,}', lsb_data)
    if strings:
        print("[*] Readable strings in LSB:")
        for s in strings[:10]:
            print(f"    {s.decode('utf-8', errors='ignore')}")

def check_spectral_analysis(filepath):
    """Check for spectral steganography"""
    print("\n[*] Checking for spectral steganography...")
    print("[!] Note: Install 'pip install scipy numpy matplotlib' for full spectral analysis")
    
    try:
        import numpy as np
        from scipy.io import wavfile
        import subprocess
        
        # Convert MP3 to WAV using ffmpeg if available
        wav_file = "temp_audio.wav"
        result = subprocess.run(['ffmpeg', '-i', filepath, '-ar', '44100', wav_file, '-y'], 
                              capture_output=True, text=True)
        
        if os.path.exists(wav_file):
            print("[+] Converted to WAV for analysis")
            
            # Read WAV file
            sample_rate, audio_data = wavfile.read(wav_file)
            print(f"[*] Sample rate: {sample_rate} Hz")
            print(f"[*] Audio shape: {audio_data.shape}")
            
            # Perform FFT
            from scipy.fft import fft, fftfreq
            
            # Take first channel if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]
            
            # FFT on a segment
            segment = audio_data[:sample_rate * 10]  # First 10 seconds
            fft_data = fft(segment)
            freqs = fftfreq(len(segment), 1/sample_rate)
            
            # Look for unusual patterns in high frequencies
            high_freq_idx = np.where(freqs > 15000)[0]
            if len(high_freq_idx) > 0:
                high_freq_data = np.abs(fft_data[high_freq_idx])
                if np.max(high_freq_data) > np.mean(high_freq_data) * 10:
                    print("[+] Unusual high-frequency content detected!")
            
            os.remove(wav_file)
        else:
            print("[-] Could not convert to WAV (ffmpeg not available)")
    except ImportError:
        print("[-] scipy/numpy not available for spectral analysis")
    except Exception as e:
        print(f"[-] Spectral analysis error: {e}")

def check_metadata_tools(filepath):
    """Use exiftool-like analysis"""
    print("\n[*] Checking metadata with exiftool...")
    import subprocess
    
    try:
        result = subprocess.run(['exiftool', filepath], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            
            # Look for flag in metadata
            if 'Kaal{' in result.stdout:
                import re
                flags = re.findall(r'Kaal\{[^}]+\}', result.stdout)
                if flags:
                    print(f"\n[+] FLAG IN METADATA: {flags[0]}")
        else:
            print("[-] exiftool not available")
    except FileNotFoundError:
        print("[-] exiftool not installed")

def check_end_of_file(filepath):
    """Check the very end of the file for hidden data"""
    print("\n[*] Checking end of file...")
    
    with open(filepath, 'rb') as f:
        f.seek(-10000, 2)  # Seek to 10KB before end
        tail_data = f.read()
    
    print(f"[*] Last 200 bytes (hex):")
    print(binascii.hexlify(tail_data[-200:]).decode())
    
    print(f"\n[*] Last 200 bytes (raw):")
    print(tail_data[-200:])
    
    # Search for flag
    import re
    flags = re.findall(b'Kaal\\{[^}]+\\}', tail_data)
    if flags:
        print(f"\n[+] FLAG AT END OF FILE: {flags[0].decode('utf-8', errors='ignore')}")

def check_frame_headers(filepath):
    """Analyze MP3 frame headers for hidden data"""
    print("\n[*] Analyzing MP3 frame headers...")
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Skip ID3
    offset = 0
    if data[:3] == b'ID3':
        size_bytes = data[6:10]
        tag_size = (size_bytes[0] << 21) | (size_bytes[1] << 14) | (size_bytes[2] << 7) | size_bytes[3]
        offset = 10 + tag_size
    
    # Find MP3 frames (start with 0xFF 0xFB or 0xFF 0xFA)
    frame_count = 0
    pos = offset
    hidden_bits = []
    
    while pos < len(data) - 4:
        if data[pos] == 0xFF and (data[pos+1] & 0xE0) == 0xE0:
            # Found frame sync
            frame_count += 1
            
            # Check for unusual bits in frame header
            header = struct.unpack('>I', data[pos:pos+4])[0]
            
            # Extract potential hidden data from reserved bits
            # Bit 20 is reserved and should be 0
            if (header >> 20) & 1:
                hidden_bits.append(1)
            else:
                hidden_bits.append(0)
            
            # Skip to next frame (rough estimate)
            pos += 417  # Average MP3 frame size for 128kbps
        else:
            pos += 1
    
    print(f"[*] Found {frame_count} MP3 frames")
    
    if hidden_bits:
        # Convert bits to bytes
        hidden_bytes = []
        for i in range(0, len(hidden_bits) - 8, 8):
            byte_val = 0
            for j in range(8):
                byte_val = (byte_val << 1) | hidden_bits[i + j]
            hidden_bytes.append(byte_val)
        
        hidden_data = bytes(hidden_bytes)
        print(f"[*] Extracted {len(hidden_data)} bytes from frame headers")
        
        # Search for flag
        import re
        flags = re.findall(b'Kaal\\{[^}]+\\}', hidden_data)
        if flags:
            print(f"[+] FLAG IN FRAME HEADERS: {flags[0].decode('utf-8', errors='ignore')}")

def main():
    mp3_file = "chall_media/chall_media.mp3"
    
    if not os.path.exists(mp3_file):
        print(f"[-] File not found: {mp3_file}")
        return
    
    print("="*60)
    print("DEEP AUDIO STEGANOGRAPHY ANALYSIS")
    print("="*60)
    
    extract_lsb_from_audio(mp3_file)
    check_end_of_file(mp3_file)
    check_frame_headers(mp3_file)
    check_spectral_analysis(mp3_file)
    check_metadata_tools(mp3_file)
    
    print("\n" + "="*60)
    print("[*] Deep analysis complete!")
    print("="*60)

if __name__ == "__main__":
    main()
