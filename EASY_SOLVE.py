#!/usr/bin/env python3
"""
For an EASY audio forensics challenge, the flag is usually:
1. In the spectrogram (visual)
2. Reversed audio
3. LSB steganography
4. Metadata
5. Appended data
"""

import wave
import struct

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== EASY AUDIO FORENSICS SOLVE ===\n")

# Read file
with open(wav_path, 'rb') as f:
    raw = f.read()

print(f"File size: {len(raw)} bytes")

# Check 1: Metadata/strings
print("\n[1] Checking for plaintext flag...")
if b'Kaal{' in raw:
    pos = raw.find(b'Kaal{')
    flag = raw[pos:pos+50]
    print(f"FOUND: {flag}")

# Check 2: End of file
print("\n[2] Checking end of file...")
print(f"Last 500 bytes: {raw[-500:]}")

# Check 3: After data chunk
with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    
data_pos = raw.find(b'data')
if data_pos != -1:
    data_size = struct.unpack('<I', raw[data_pos+4:data_pos+8])[0]
    expected_end = data_pos + 8 + data_size
    if expected_end < len(raw):
        extra = raw[expected_end:]
        print(f"\n[3] Extra data after audio: {len(extra)} bytes")
        print(extra)
        if b'Kaal{' in extra:
            print("FLAG IN EXTRA DATA!")

# Check 4: Simple LSB
print("\n[4] Checking LSB...")
samples = struct.unpack(f'<{len(frames)//2}h', frames)
lsb_bits = [s & 1 for s in samples[:8000]]  # First 1000 bytes worth
lsb_bytes = bytes([sum([lsb_bits[i*8+j] << j for j in range(8)]) for i in range(len(lsb_bits)//8)])
print(f"First 100 LSB bytes: {lsb_bytes[:100]}")
if b'Kaal{' in lsb_bytes:
    pos = lsb_bytes.find(b'Kaal{')
    print(f"FLAG IN LSB: {lsb_bytes[pos:pos+50]}")

# Check 5: Spectrogram hint
print("\n[5] Check spectrogram.png for visual flag!")
print("    Open it and look for text written in the frequency domain")

print("\n[6] Play reversed.wav to hear if message is reversed")

print("\nIf none of these work, the flag is likely in the SPECTROGRAM IMAGE.")
print("Open spectrogram.png and look carefully!")
