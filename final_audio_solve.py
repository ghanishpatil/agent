import wave
import struct

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Final Comprehensive Analysis ===\n")

# Read raw file
with open(wav_path, 'rb') as f:
    raw_data = f.read()

# Check if this is actually a different file type
print("1. Checking file signature...")
print(f"First 16 bytes: {raw_data[:16]}")
print(f"Hex: {raw_data[:16].hex()}")

# RIFF files can contain different data
# Check if the WAVE format is correct or if it should be something else

# Read as WAV
with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    params = wav.getparams()

print(f"\nWAV parameters: {params}")

# The challenge says "one small mistake" - maybe a single bit or byte is flipped
# Let's check if flipping each byte in the header reveals something

print("\n2. Checking for single-byte errors in header...")

# Try flipping each byte in the first 100 bytes
for i in range(100):
    test_data = bytearray(raw_data)
    # Try different modifications
    for modification in [1, 2, 4, 8, 16, 32, 64, 128]:  # Single bit flips
        test_data[i] = raw_data[i] ^ modification
        
        # Check if this creates a valid pattern
        if b'Kaal{' in test_data:
            print(f"✓ Found flag by flipping bit at position {i}!")
            pos = test_data.find(b'Kaal{')
            end = test_data.find(b'}', pos)
            if end != -1:
                flag = test_data[pos:end+1].decode('ascii', errors='ignore')
                print(f"\nFLAG: {flag}")
                break
    else:
        continue
    break

# Check if the audio data itself contains the flag when interpreted differently
print("\n3. Checking audio data interpretations...")

samples = struct.unpack(f'<{len(frames)//2}h', frames)

# Try treating pairs of samples as characters
print("\nTrying sample pairs as ASCII...")
for offset in range(10):
    chars = []
    for i in range(offset, len(samples)-1, 2):
        # Combine two samples into a character
        val = (samples[i] + samples[i+1]) & 0xFF
        if 32 <= val <= 126:
            chars.append(chr(val))
        else:
            chars.append('.')
    
    text = ''.join(chars[:1000])
    if 'Kaal{' in text:
        print(f"✓ Found with offset {offset}!")
        pos = text.find('Kaal{')
        end = text.find('}', pos)
        if end != -1:
            print(f"\nFLAG: {text[pos:end+1]}")
            break

# Check if samples encode characters directly (not LSB)
print("\n4. Direct sample-to-character mapping...")
# Sometimes audio samples directly represent ASCII values
for scale in [1, 10, 100, 256]:
    chars = []
    for sample in samples:
        val = (abs(sample) // scale) & 0xFF
        if 32 <= val <= 126:
            chars.append(chr(val))
    
    text = ''.join(chars)
    if 'Kaal{' in text:
        print(f"✓ Found with scale {scale}!")
        pos = text.find('Kaal{')
        end = text.find('}', pos)
        if end != -1:
            print(f"\nFLAG: {text[pos:end+1]}")
            break

# Check for interleaved data
print("\n5. Checking interleaved encoding...")
# Maybe flag is in alternating bytes
for start in range(2):
    interleaved = frames[start::2]
    if b'Kaal{' in interleaved:
        print(f"✓ Found in interleaved data (start={start})!")
        pos = interleaved.find(b'Kaal{')
        end = interleaved.find(b'}', pos)
        if end != -1:
            flag = interleaved[pos:end+1].decode('ascii', errors='ignore')
            print(f"\nFLAG: {flag}")
            break

# Check if the "mistake" is in the filename - maybe it's not a WAV
print("\n6. Trying to interpret as other formats...")
# Check if it's actually a ZIP, PNG, or other format with wrong extension
magic_numbers = {
    b'PK\x03\x04': 'ZIP',
    b'\x89PNG': 'PNG',
    b'GIF8': 'GIF',
    b'\xFF\xD8\xFF': 'JPEG',
    b'%PDF': 'PDF',
}

for magic, format_name in magic_numbers.items():
    if raw_data.startswith(magic):
        print(f"! File is actually {format_name}, not WAV!")
        # Try to extract
        with open(f'chall_extracted.{format_name.lower()}', 'wb') as f:
            f.write(raw_data)
        print(f"Saved as chall_extracted.{format_name.lower()}")

# Look for embedded files
print("\n7. Searching for embedded files...")
for magic, format_name in magic_numbers.items():
    pos = raw_data.find(magic)
    if pos > 0:  # Not at start
        print(f"! Found {format_name} embedded at position {pos}!")
        embedded = raw_data[pos:]
        with open(f'embedded.{format_name.lower()}', 'wb') as f:
            f.write(embedded)
        print(f"Saved as embedded.{format_name.lower()}")
        
        # Check if it contains the flag
        if b'Kaal{' in embedded:
            flag_pos = embedded.find(b'Kaal{')
            end = embedded.find(b'}', flag_pos)
            if end != -1:
                flag = embedded[flag_pos:end+1].decode('ascii', errors='ignore')
                print(f"\n✓ FLAG FOUND: {flag}")

print("\n=== Analysis Complete ===")
