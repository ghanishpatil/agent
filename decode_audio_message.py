import wave
import struct

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Decoding Audio as Data ===\n")

with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    sample_rate = wav.getframerate()
    n_channels = wav.getnchannels()
    sampwidth = wav.getsampwidth()

print(f"Sample rate: {sample_rate} Hz")
print(f"Channels: {n_channels}")
print(f"Sample width: {sampwidth} bytes")
print(f"Total frames: {len(frames)//2}")

# Try interpreting audio samples as ASCII
print("\n1. Trying to decode samples as ASCII characters...")
samples = struct.unpack(f'<{len(frames)//2}h', frames)

# Method 1: Take low byte of each sample
ascii_chars = []
for sample in samples:
    # Get the low byte
    low_byte = sample & 0xFF
    if 32 <= low_byte <= 126:  # Printable ASCII
        ascii_chars.append(chr(low_byte))
    else:
        ascii_chars.append('.')

ascii_text = ''.join(ascii_chars)
print(f"First 500 characters: {ascii_text[:500]}")

if 'Kaal{' in ascii_text:
    pos = ascii_text.find('Kaal{')
    print(f"\n✓ Found flag at position {pos}!")
    end_pos = ascii_text.find('}', pos)
    if end_pos != -1:
        flag = ascii_text[pos:end_pos+1]
        print(f"\nFLAG: {flag}")

# Method 2: Take high byte of each sample
print("\n2. Trying high byte of samples...")
ascii_chars_high = []
for sample in samples:
    high_byte = (sample >> 8) & 0xFF
    if 32 <= high_byte <= 126:
        ascii_chars_high.append(chr(high_byte))
    else:
        ascii_chars_high.append('.')

ascii_text_high = ''.join(ascii_chars_high)
print(f"First 500 characters: {ascii_text_high[:500]}")

if 'Kaal{' in ascii_text_high:
    pos = ascii_text_high.find('Kaal{')
    print(f"\n✓ Found flag at position {pos}!")
    end_pos = ascii_text_high.find('}', pos)
    if end_pos != -1:
        flag = ascii_text_high[pos:end_pos+1]
        print(f"\nFLAG: {flag}")

# Method 3: Decode every Nth sample
print("\n3. Trying to decode every 8th sample...")
for step in [8, 16, 32, 64]:
    chars = []
    for i in range(0, len(samples), step):
        byte_val = samples[i] & 0xFF
        if 32 <= byte_val <= 126:
            chars.append(chr(byte_val))
    
    text = ''.join(chars)
    if 'Kaal{' in text:
        print(f"\n✓ Found flag with step={step}!")
        pos = text.find('Kaal{')
        end_pos = text.find('}', pos)
        if end_pos != -1:
            flag = text[pos:end_pos+1]
            print(f"\nFLAG: {flag}")
            break

# Method 4: Check if samples encode binary data that spells out text
print("\n4. Checking for binary-encoded text...")
# Group samples into bytes
for offset in range(8):
    binary_str = ''
    for i in range(offset, min(offset + 1000, len(samples))):
        binary_str += str(samples[i] & 1)
    
    # Convert binary to bytes
    bytes_data = []
    for i in range(0, len(binary_str), 8):
        if i + 8 <= len(binary_str):
            byte_val = int(binary_str[i:i+8], 2)
            bytes_data.append(byte_val)
    
    text = bytes(bytes_data).decode('ascii', errors='ignore')
    if 'Kaal' in text:
        print(f"✓ Found flag with offset={offset}!")
        print(f"Text: {text[:200]}")

# Method 5: Check raw frame data directly
print("\n5. Checking raw frame data...")
if b'Kaal{' in frames:
    pos = frames.find(b'Kaal{')
    print(f"✓ Found 'Kaal{{' in raw frames at position {pos}!")
    end_pos = frames.find(b'}', pos)
    if end_pos != -1:
        flag = frames[pos:end_pos+1].decode('ascii', errors='ignore')
        print(f"\nFLAG: {flag}")
    else:
        print(f"Flag area: {frames[pos:pos+100]}")

# Method 6: Check for reversed flag
if b'}' in frames and b'laaK' in frames:
    print("\n6. Checking for reversed flag...")
    end_pos = frames.find(b'}')
    # Search backwards for 'laaK'
    search_area = frames[max(0, end_pos-100):end_pos+1]
    if b'laaK' in search_area:
        print("✓ Found reversed flag pattern!")
        # Reverse the area
        reversed_area = search_area[::-1]
        print(f"Reversed: {reversed_area}")
        if b'Kaal{' in reversed_area:
            pos = reversed_area.find(b'Kaal{')
            end = reversed_area.find(b'}', pos)
            if end != -1:
                flag = reversed_area[pos:end+1].decode('ascii', errors='ignore')
                print(f"\nFLAG: {flag}")

print("\n=== Decoding Complete ===")
