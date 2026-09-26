import wave
import struct
import numpy as np

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Spectral and Deep Analysis ===\n")

# Read audio
with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    sample_rate = wav.getframerate()

samples = np.frombuffer(frames, dtype=np.int16)

print(f"Samples: {len(samples)}")
print(f"Sample rate: {sample_rate} Hz")

# Check if there's a pattern in sample values themselves
print("\n1. Analyzing sample value distribution...")
unique_samples = np.unique(samples)
print(f"Unique sample values: {len(unique_samples)}")

# Check if samples cluster around ASCII values
ascii_range_samples = samples[(samples >= 32) & (samples <= 126)]
print(f"Samples in ASCII range (32-126): {len(ascii_range_samples)}")

if len(ascii_range_samples) > 100:
    print("Trying to decode samples as ASCII...")
    ascii_text = ''.join([chr(s) for s in ascii_range_samples[:1000]])
    print(f"Text: {ascii_text[:200]}")
    
    if 'Kaal{' in ascii_text:
        pos = ascii_text.find('Kaal{')
        end = ascii_text.find('}', pos)
        if end != -1:
            print(f"\n✓ FLAG: {ascii_text[pos:end+1]}")

# Check for patterns in sample sequence
print("\n2. Looking for repeating patterns...")
# Check if every Nth sample forms a message
for n in [7, 8, 9, 10, 11, 12, 16, 32]:
    selected = samples[::n]
    # Try as ASCII
    ascii_vals = selected[(selected >= 32) & (selected <= 126)]
    if len(ascii_vals) > 20:
        text = ''.join([chr(s) for s in ascii_vals])
        if 'Kaal' in text or 'flag' in text.lower():
            print(f"\n✓ Found pattern with n={n}!")
            print(f"Text: {text}")
            if 'Kaal{' in text:
                pos = text.find('Kaal{')
                end = text.find('}', pos)
                if end != -1:
                    print(f"\nFLAG: {text[pos:end+1]}")

# Check if the "mistake" is that samples are offset by a constant
print("\n3. Checking for offset/shift in sample values...")
for offset in [-128, -64, -32, -16, -8, -4, -2, -1, 1, 2, 4, 8, 16, 32, 64, 128]:
    shifted = samples + offset
    ascii_range = shifted[(shifted >= 32) & (shifted <= 126)]
    
    if len(ascii_range) > 100:
        text = ''.join([chr(s) for s in ascii_range[:2000]])
        if 'Kaal{' in text:
            print(f"\n✓ Found with offset {offset}!")
            pos = text.find('Kaal{')
            end = text.find('}', pos)
            if end != -1:
                print(f"\nFLAG: {text[pos:end+1]}")
                break

# Check if samples need to be divided/scaled
print("\n4. Checking for scaling issues...")
for divisor in [2, 4, 8, 16, 32, 64, 128, 256]:
    scaled = samples // divisor
    ascii_range = scaled[(scaled >= 32) & (scaled <= 126)]
    
    if len(ascii_range) > 100:
        text = ''.join([chr(s) for s in ascii_range[:2000]])
        if 'Kaal{' in text:
            print(f"\n✓ Found with divisor {divisor}!")
            pos = text.find('Kaal{')
            end = text.find('}', pos)
            if end != -1:
                print(f"\nFLAG: {text[pos:end+1]}")
                break

# Check if we need to take absolute value and scale
print("\n5. Checking absolute value with scaling...")
abs_samples = np.abs(samples)
for divisor in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]:
    scaled = abs_samples // divisor
    ascii_range = scaled[(scaled >= 32) & (scaled <= 126)]
    
    if len(ascii_range) > 100:
        text = ''.join([chr(s) for s in ascii_range[:2000]])
        if 'Kaal{' in text:
            print(f"\n✓ Found with abs() and divisor {divisor}!")
            pos = text.find('Kaal{')
            end = text.find('}', pos)
            if end != -1:
                print(f"\nFLAG: {text[pos:end+1]}")
                break

# Try modulo operations
print("\n6. Checking modulo operations...")
for mod in [128, 256, 512]:
    modded = samples % mod
    ascii_range = modded[(modded >= 32) & (modded <= 126)]
    
    if len(ascii_range) > 100:
        text = ''.join([chr(s) for s in ascii_range[:2000]])
        if 'Kaal{' in text:
            print(f"\n✓ Found with modulo {mod}!")
            pos = text.find('Kaal{')
            end = text.find('}', pos)
            if end != -1:
                print(f"\nFLAG: {text[pos:end+1]}")
                break

# Check if we need to XOR samples
print("\n7. Checking XOR operations...")
for xor_val in [0x80, 0x8000, 0xFF, 0xFFFF]:
    xored = samples ^ xor_val
    ascii_range = xored[(xored >= 32) & (xored <= 126)]
    
    if len(ascii_range) > 100:
        text = ''.join([chr(s) for s in ascii_range[:2000]])
        if 'Kaal{' in text:
            print(f"\n✓ Found with XOR {hex(xor_val)}!")
            pos = text.find('Kaal{')
            end = text.find('}', pos)
            if end != -1:
                print(f"\nFLAG: {text[pos:end+1]}")
                break

print("\n=== Analysis Complete ===")
