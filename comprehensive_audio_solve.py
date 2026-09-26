import wave
import numpy as np
import struct

audio_path = r"D:\mission-git-hackss\chall.wav"

print("=" * 60)
print("COMPREHENSIVE AUDIO FORENSICS")
print("=" * 60)

# Read raw file
with open(audio_path, 'rb') as f:
    all_data = f.read()

# Parse WAV manually
riff = all_data[:4]
file_size = struct.unpack('<I', all_data[4:8])[0]
wave_marker = all_data[8:12]

print(f"RIFF: {riff}")
print(f"File size: {file_size}")
print(f"WAVE: {wave_marker}")

# Find all chunks
pos = 12
chunks = []
while pos < len(all_data) - 8:
    chunk_id = all_data[pos:pos+4]
    chunk_size = struct.unpack('<I', all_data[pos+4:pos+8])[0]
    chunks.append((chunk_id, pos, chunk_size))
    print(f"\nChunk: {chunk_id} at {pos}, size {chunk_size}")
    
    if chunk_id == b'fmt ':
        fmt_data = all_data[pos+8:pos+8+chunk_size]
        audio_format = struct.unpack('<H', fmt_data[0:2])[0]
        num_channels = struct.unpack('<H', fmt_data[2:4])[0]
        sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
        byte_rate = struct.unpack('<I', fmt_data[8:12])[0]
        block_align = struct.unpack('<H', fmt_data[12:14])[0]
        bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
        
        print(f"  Format: {audio_format} (1=PCM)")
        print(f"  Channels: {num_channels}")
        print(f"  Sample Rate: {sample_rate} Hz")
        print(f"  Byte Rate: {byte_rate}")
        print(f"  Block Align: {block_align}")
        print(f"  Bits/Sample: {bits_per_sample}")
    
    elif chunk_id == b'data':
        data_start = pos + 8
        data_end = data_start + chunk_size
        print(f"  Audio data: {data_start} to {data_end}")
        
        # Show pattern
        print(f"  First 20 samples (hex):")
        for i in range(10):
            sample_pos = data_start + i * 2
            b1, b2 = all_data[sample_pos], all_data[sample_pos+1]
            val = struct.unpack('<h', bytes([b1, b2]))[0]
            print(f"    [{b1:02x} {b2:02x}] = {val:6d}")
    
    elif chunk_id == b'LIST':
        list_data = all_data[pos+8:pos+8+min(chunk_size, 200)]
        print(f"  Content: {list_data}")
    
    pos += 8 + chunk_size
    if chunk_size % 2 == 1:  # Chunks are word-aligned
        pos += 1

# Now let's think about the "mistake"
print("\n" + "=" * 60)
print("HYPOTHESIS: The mistake is in the LOWER BYTE")
print("=" * 60)

with wave.open(audio_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16)

print(f"Samples shape: {samples.shape}")
print(f"Sample values (first 20): {samples[:20]}")

# The samples are like: -256, 512, 4096, 10752...
# In hex: 0xFF00, 0x0200, 0x1000, 0x2A00...
# The lower byte is ALWAYS 0x00

# What if the lower byte should contain a message?
# Let's extract what SHOULD be in the lower byte by looking at the upper byte

upper_bytes = []
for sample in samples:
    # Get the upper byte (bits 8-15)
    upper = (sample >> 8) & 0xFF
    upper_bytes.append(upper)

upper_data = bytes(upper_bytes)
upper_str = upper_data.decode('latin-1', errors='ignore')

print(f"\nUpper bytes (first 200 chars):")
print(repr(upper_str[:200]))

# Look for flag
if 'Kaal{' in upper_str or 'kaal{' in upper_str.lower():
    print(f"\n🎯 FLAG IN UPPER BYTES!")
    start = upper_str.lower().find('kaal{')
    if start != -1:
        print(upper_str[start:start+100])

# Also check if the upper bytes spell out something when interpreted as ASCII
print(f"\nUpper bytes as ASCII (first 100):")
printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in upper_bytes[:100])
print(printable)

# Check for common words
common_words = ['flag', 'kaal', 'password', 'key', 'secret', 'hidden', 'message']
for word in common_words:
    if word in upper_str.lower():
        print(f"\n Found '{word}' in upper bytes!")
        idx = upper_str.lower().find(word)
        print(f"  Context: {upper_str[max(0,idx-20):idx+50]}")

# Save upper bytes to file
with open('upper_bytes.txt', 'wb') as f:
    f.write(upper_data)
print(f"\n✓ Upper bytes saved to: upper_bytes.txt")

# Check if there's a pattern - maybe it's a substitution cipher?
print("\n" + "=" * 60)
print("CHECKING FOR PATTERNS")
print("=" * 60)

# Look for repeating sequences
from collections import Counter
byte_freq = Counter(upper_bytes)
print(f"Most common bytes: {byte_freq.most_common(10)}")

# Check if it looks like text (high frequency of certain bytes)
text_like_bytes = [b for b in upper_bytes if 32 <= b < 127]
print(f"Printable ASCII bytes: {len(text_like_bytes)} / {len(upper_bytes)} ({len(text_like_bytes)/len(upper_bytes)*100:.1f}%)")
