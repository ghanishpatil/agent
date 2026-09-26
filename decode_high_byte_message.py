import wave
import struct
import re

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Decoding High Byte Message ===\n")

with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())

samples = struct.unpack(f'<{len(frames)//2}h', frames)

# Extract high byte (which contains the readable text)
high_bytes = bytes([(s >> 8) & 0xFF for s in samples])

print(f"Total high bytes: {len(high_bytes)}")

# Convert to printable text
text = ''
for byte in high_bytes:
    if 32 <= byte <= 126:
        text += chr(byte)
    else:
        text += ' '

print(f"Decoded text length: {len(text)}")
print("\nFirst 1000 characters:")
print(text[:1000])

# Search for flag patterns
print("\n=== Searching for Flag Patterns ===")

# Look for "Kaal{" or variations
if 'Kaal{' in text:
    pos = text.find('Kaal{')
    print(f"\n✓ Found 'Kaal{{' at position {pos}!")
    end = text.find('}', pos)
    if end != -1:
        flag = text[pos:end+1]
        print(f"\nFLAG: {flag}")
    else:
        print(f"Flag start: {text[pos:pos+100]}")

# Look for reversed or corrupted versions
patterns = ['laaK{', 'Kaai{', 'Kaal[', 'Kaal(', 'kaal{', 'KAAL{']
for pattern in patterns:
    if pattern in text:
        pos = text.find(pattern)
        print(f"\nFound '{pattern}' at position {pos}")
        print(f"Context: {text[max(0,pos-20):pos+100]}")

# Maybe the flag is split or has spaces
print("\n=== Looking for Split Patterns ===")
# Remove spaces and check again
no_spaces = text.replace(' ', '')
if 'Kaal{' in no_spaces:
    pos = no_spaces.find('Kaal{')
    print(f"\n✓ Found 'Kaal{{' in no-space version at position {pos}!")
    end = no_spaces.find('}', pos)
    if end != -1:
        flag = no_spaces[pos:end+1]
        print(f"\nFLAG: {flag}")

# Check if characters need to be shifted
print("\n=== Checking Character Shifts ===")
for shift in range(-5, 6):
    if shift == 0:
        continue
    shifted_text = ''
    for char in text[:5000]:
        if 'A' <= char <= 'Z':
            shifted_text += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
        elif 'a' <= char <= 'z':
            shifted_text += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
        else:
            shifted_text += char
    
    if 'Kaal{' in shifted_text:
        print(f"\n✓ Found with shift {shift}!")
        pos = shifted_text.find('Kaal{')
        end = shifted_text.find('}', pos)
        if end != -1:
            flag = shifted_text[pos:end+1]
            print(f"\nFLAG: {flag}")
            break

# Check if we need to XOR the high bytes
print("\n=== Checking XOR on High Bytes ===")
for xor_key in range(1, 256):
    xored = bytes([b ^ xor_key for b in high_bytes])
    if b'Kaal{' in xored:
        print(f"\n✓ Found with XOR key {xor_key} (0x{xor_key:02x})!")
        pos = xored.find(b'Kaal{')
        end = xored.find(b'}', pos)
        if end != -1:
            flag = xored[pos:end+1].decode('ascii', errors='ignore')
            print(f"\nFLAG: {flag}")
            break

# Save the high byte text for manual inspection
with open('high_byte_text.txt', 'w', encoding='utf-8', errors='ignore') as f:
    f.write(text)
print("\n✓ Saved high byte text to high_byte_text.txt")

print("\n=== Decode Complete ===")
