#!/usr/bin/env python3
"""
Decode audio samples - maybe the flag is encoded in the amplitude values
"""

import struct
import re

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

# Get audio data
data_pos = data.find(b'data')
data_size = struct.unpack('<I', data[data_pos+4:data_pos+8])[0]
audio_data = data[data_pos+8:data_pos+8+data_size]

print(f"[*] Audio data size: {data_size} bytes")
print(f"[*] Number of 16-bit samples: {data_size // 2}")

# Read as 16-bit samples
samples = []
for i in range(0, min(len(audio_data), 100000), 2):
    if i+1 < len(audio_data):
        sample = struct.unpack('<h', audio_data[i:i+2])[0]
        samples.append(sample)

print(f"[*] Read {len(samples)} samples")

# Method 1: Check if samples encode ASCII directly
print("\n[1] Checking if samples encode ASCII...")
ascii_chars = []
for sample in samples[:1000]:
    # Normalize to 0-255 range
    normalized = (sample + 32768) // 256
    if 32 <= normalized < 127:
        ascii_chars.append(chr(normalized))

if ascii_chars:
    text = ''.join(ascii_chars)
    print(f"    Text from samples: {text[:200]}")
    
    flags = re.findall(r'Kaal\{[^}]+\}', text)
    if flags:
        print(f"\n[+] *** FLAG FROM SAMPLES ***: {flags[0]}")

# Method 2: Check low byte of samples
print("\n[2] Checking low bytes of samples...")
low_bytes = []
for sample in samples[:50000]:
    low_byte = sample & 0xFF
    low_bytes.append(low_byte)

low_byte_data = bytes(low_bytes)
flags = re.findall(rb'Kaal\{[^}]+\}', low_byte_data)
if flags:
    for flag in flags:
        print(f"[+] *** FLAG IN LOW BYTES ***: {flag.decode('utf-8', errors='ignore')}")

# Check for readable text
readable = re.findall(rb'[\x20-\x7e]{15,}', low_byte_data)
if readable:
    print(f"    Readable text in low bytes:")
    for s in readable[:20]:
        decoded = s.decode('utf-8', errors='ignore')
        print(f"        {decoded}")

# Method 3: Check high byte of samples
print("\n[3] Checking high bytes of samples...")
high_bytes = []
for sample in samples[:50000]:
    high_byte = (sample >> 8) & 0xFF
    high_bytes.append(high_byte)

high_byte_data = bytes(high_bytes)
flags = re.findall(rb'Kaal\{[^}]+\}', high_byte_data)
if flags:
    for flag in flags:
        print(f"[+] *** FLAG IN HIGH BYTES ***: {flag.decode('utf-8', errors='ignore')}")

# Check for readable text
readable = re.findall(rb'[\x20-\x7e]{15,}', high_byte_data)
if readable:
    print(f"    Readable text in high bytes:")
    for s in readable[:20]:
        decoded = s.decode('utf-8', errors='ignore')
        print(f"        {decoded}")

# Method 4: Delta encoding - check differences between samples
print("\n[4] Checking delta encoding...")
deltas = []
for i in range(1, min(len(samples), 50000)):
    delta = samples[i] - samples[i-1]
    # Normalize to byte range
    delta_byte = (delta + 128) & 0xFF
    deltas.append(delta_byte)

delta_data = bytes(deltas)
flags = re.findall(rb'Kaal\{[^}]+\}', delta_data)
if flags:
    for flag in flags:
        print(f"[+] *** FLAG IN DELTAS ***: {flag.decode('utf-8', errors='ignore')}")

# Method 5: Check if zero samples spell something
print("\n[5] Checking zero-crossing patterns...")
zero_crossings = []
for i in range(1, min(len(samples), 10000)):
    if (samples[i-1] < 0 and samples[i] >= 0) or (samples[i-1] >= 0 and samples[i] < 0):
        zero_crossings.append(1)
    else:
        zero_crossings.append(0)

# Convert to bytes
zc_bytes = []
for i in range(0, len(zero_crossings), 8):
    if i + 7 < len(zero_crossings):
        byte_val = 0
        for j in range(8):
            byte_val = (byte_val << 1) | zero_crossings[i + j]
        zc_bytes.append(byte_val)

zc_data = bytes(zc_bytes)
flags = re.findall(rb'Kaal\{[^}]+\}', zc_data)
if flags:
    for flag in flags:
        print(f"[+] *** FLAG IN ZERO CROSSINGS ***: {flag.decode('utf-8', errors='ignore')}")

# Method 6: Check every Nth sample
print("\n[6] Checking every Nth sample...")
for n in [2, 3, 4, 5, 8, 10, 16, 32]:
    nth_samples = samples[::n][:5000]
    
    # Convert to bytes (low byte)
    nth_bytes = bytes([s & 0xFF for s in nth_samples])
    
    flags = re.findall(rb'Kaal\{[^}]+\}', nth_bytes)
    if flags:
        for flag in flags:
            print(f"[+] *** FLAG IN EVERY {n}TH SAMPLE ***: {flag.decode('utf-8', errors='ignore')}")

print("\n[*] Analysis complete!")
