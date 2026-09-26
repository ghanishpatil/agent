import wave
import numpy as np

audio_path = r"D:\mission-git-hackss\chall.wav"

with wave.open(audio_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16)

# Extract upper byte (the actual audio data)
upper_bytes = [(sample >> 8) & 0xFF for sample in samples]

# Convert to signed
upper_signed = [b if b < 128 else b - 256 for b in upper_bytes]

print("=" * 60)
print("SEARCHING FOR HIDDEN MESSAGE")
print("=" * 60)

# Method 1: Look at the upper bytes as direct ASCII
upper_data = bytes(upper_bytes)
print(f"\nMethod 1: Direct ASCII interpretation")
print(f"First 500 bytes:")
print(upper_data[:500])

# Method 2: Look for specific patterns
print(f"\n" + "=" * 60)
print("SEARCHING FOR 'Kaal' PATTERN")
print("=" * 60)

# Search for 'Kaal' in various forms
target = b'Kaal{'
for i in range(len(upper_data) - len(target)):
    if upper_data[i:i+len(target)] == target:
        print(f"Found 'Kaal{{' at position {i}!")
        print(f"Context: {upper_data[i:i+50]}")

# Try case-insensitive
target_lower = b'kaal{'
for i in range(len(upper_data) - len(target_lower)):
    if upper_data[i:i+len(target_lower)].lower() == target_lower:
        print(f"Found 'kaal{{' (case-insensitive) at position {i}!")
        print(f"Context: {upper_data[i:i+50]}")

# Method 3: Maybe it's XORed or shifted?
print(f"\n" + "=" * 60)
print("TRYING XOR/SHIFT OPERATIONS")
print("=" * 60)

# Try XOR with common values
for xor_key in [0x00, 0xFF, 0x20, 0x40, 0x80, 0xAA, 0x55]:
    xored = bytes([b ^ xor_key for b in upper_bytes])
    if b'Kaal{' in xored or b'kaal{' in xored.lower():
        print(f"\n🎯 FOUND WITH XOR KEY 0x{xor_key:02x}!")
        start = xored.lower().find(b'kaal{')
        if start != -1:
            print(f"Flag: {xored[start:start+50]}")

# Method 4: Maybe every Nth byte?
print(f"\n" + "=" * 60)
print("TRYING STRIDE PATTERNS")
print("=" * 60)

for stride in [2, 3, 4, 5, 8, 10]:
    for offset in range(stride):
        strided = bytes(upper_bytes[offset::stride])
        if b'Kaal{' in strided or b'kaal{' in strided.lower():
            print(f"\n🎯 FOUND WITH STRIDE {stride}, OFFSET {offset}!")
            start = strided.lower().find(b'kaal{')
            if start != -1:
                print(f"Flag: {strided[start:start+50]}")

# Method 5: Check if it's in the LOWER byte position (which is all 0s)
# Maybe we need to WRITE something there?
print(f"\n" + "=" * 60)
print("ANALYZING THE ZERO LOWER BYTE")
print("=" * 60)

print("The lower byte is ALL zeros. This is the 'mistake'.")
print("Possible interpretations:")
print("1. The lower byte should contain the upper byte (duplicate)")
print("2. The lower byte should contain a message")
print("3. The bytes should be swapped")
print("4. The audio should be shifted right by 8 bits")

# Let's try to see if there's a message when we interpret the samples differently
print(f"\n" + "=" * 60)
print("ALTERNATIVE INTERPRETATION")
print("=" * 60)

# What if we're supposed to read it as 8-bit samples instead of 16-bit?
samples_8bit = np.frombuffer(frames, dtype=np.uint8)
print(f"As 8-bit samples: {len(samples_8bit)} samples")
print(f"First 100: {samples_8bit[:100]}")

# Every other byte is 0x00, the others have data
non_zero = samples_8bit[samples_8bit != 0]
print(f"\nNon-zero bytes: {len(non_zero)}")
print(f"First 100 non-zero: {non_zero[:100]}")

non_zero_data = bytes(non_zero)
print(f"\nAs string: {non_zero_data[:200]}")

if b'Kaal{' in non_zero_data or b'kaal{' in non_zero_data.lower():
    print(f"\n🎯 FLAG IN NON-ZERO BYTES!")
    start = non_zero_data.lower().find(b'kaal{')
    if start != -1:
        print(f"Flag: {non_zero_data[start:start+50]}")

# Check for ROT13 or Caesar cipher
print(f"\n" + "=" * 60)
print("TRYING CAESAR CIPHER")
print("=" * 60)

for shift in range(1, 26):
    shifted = bytes([(b + shift) % 256 if 32 <= b < 127 else b for b in upper_bytes])
    if b'Kaal{' in shifted or b'kaal{' in shifted.lower():
        print(f"\n🎯 FOUND WITH CAESAR SHIFT {shift}!")
        start = shifted.lower().find(b'kaal{')
        if start != -1:
            print(f"Flag: {shifted[start:start+50]}")
