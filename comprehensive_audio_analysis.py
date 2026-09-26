import wave
import struct
import os

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Comprehensive Audio Analysis ===\n")

# Read the entire file
with open(wav_path, 'rb') as f:
    raw_data = f.read()

# Check for reversed audio (play backwards)
print("1. Checking if audio needs to be reversed...")
with wave.open(wav_path, 'rb') as wav:
    params = wav.getparams()
    frames = wav.readframes(wav.getnframes())
    
# Reverse the audio samples
samples = struct.unpack(f'<{len(frames)//2}h', frames)
reversed_samples = samples[::-1]
reversed_frames = struct.pack(f'<{len(reversed_samples)}h', *reversed_samples)

# Save reversed audio
reversed_path = 'chall_reversed.wav'
with wave.open(reversed_path, 'wb') as wav_out:
    wav_out.setparams(params)
    wav_out.writeframes(reversed_frames)
print(f"✓ Saved reversed audio to {reversed_path}")

# Check metadata in LIST chunk
print("\n2. Checking LIST/INFO metadata...")
list_pos = raw_data.find(b'LIST')
if list_pos != -1:
    list_size = struct.unpack('<I', raw_data[list_pos+4:list_pos+8])[0]
    list_data = raw_data[list_pos+8:list_pos+8+list_size]
    print(f"LIST chunk data: {list_data}")
    
    # Look for hidden text in metadata
    if b'Kaal{' in list_data:
        print("✓ Found flag in metadata!")
        pos = list_data.find(b'Kaal{')
        print(f"Flag: {list_data[pos:pos+50]}")

# Check for phase encoding or inverted samples
print("\n3. Checking for inverted samples...")
inverted_samples = [-s for s in samples]
inverted_frames = struct.pack(f'<{len(inverted_samples)}h', *inverted_samples)

inverted_path = 'chall_inverted.wav'
with wave.open(inverted_path, 'wb') as wav_out:
    wav_out.setparams(params)
    wav_out.writeframes(inverted_frames)
print(f"✓ Saved inverted audio to {inverted_path}")

# Check for data after the audio
print("\n4. Checking for appended data...")
data_chunk_pos = raw_data.find(b'data')
if data_chunk_pos != -1:
    data_size = struct.unpack('<I', raw_data[data_chunk_pos+4:data_chunk_pos+8])[0]
    expected_end = data_chunk_pos + 8 + data_size
    
    if expected_end < len(raw_data):
        extra_data = raw_data[expected_end:]
        print(f"Found {len(extra_data)} bytes after audio data")
        print(f"Extra data: {extra_data}")
        
        if b'Kaal{' in extra_data:
            print("✓ Found flag in appended data!")
            pos = extra_data.find(b'Kaal{')
            end_pos = extra_data.find(b'}', pos)
            if end_pos != -1:
                flag = extra_data[pos:end_pos+1].decode('ascii', errors='ignore')
                print(f"Flag: {flag}")

# Check for wrong byte order (big endian vs little endian)
print("\n5. Checking byte order issues...")
# Try reading as big-endian
samples_be = struct.unpack(f'>{len(frames)//2}h', frames)
be_frames = struct.pack(f'<{len(samples_be)}h', *samples_be)

be_path = 'chall_bigendian.wav'
with wave.open(be_path, 'wb') as wav_out:
    wav_out.setparams(params)
    wav_out.writeframes(be_frames)
print(f"✓ Saved big-endian corrected audio to {be_path}")

# Check for byte swap
print("\n6. Checking for byte swap...")
swapped_data = bytearray(frames)
for i in range(0, len(swapped_data)-1, 2):
    swapped_data[i], swapped_data[i+1] = swapped_data[i+1], swapped_data[i]

swapped_path = 'chall_swapped.wav'
with wave.open(swapped_path, 'wb') as wav_out:
    wav_out.setparams(params)
    wav_out.writeframes(bytes(swapped_data))
print(f"✓ Saved byte-swapped audio to {swapped_path}")

# Search for text in raw audio data
print("\n7. Searching for text patterns in audio data...")
# Look for ASCII text in the audio samples
text_candidates = []
for i in range(len(frames) - 100):
    chunk = frames[i:i+100]
    try:
        text = chunk.decode('ascii')
        if 'Kaal' in text or 'flag' in text.lower():
            text_candidates.append((i, text))
    except:
        pass

if text_candidates:
    print(f"Found {len(text_candidates)} text candidates:")
    for pos, text in text_candidates[:5]:
        print(f"  Position {pos}: {text[:50]}")

# Check for XOR encoding
print("\n8. Checking for XOR patterns...")
for key in range(1, 256):
    xor_data = bytes([b ^ key for b in frames[:1000]])
    if b'Kaal{' in xor_data:
        print(f"✓ Found flag with XOR key {key}!")
        full_xor = bytes([b ^ key for b in frames])
        pos = full_xor.find(b'Kaal{')
        end_pos = full_xor.find(b'}', pos)
        if end_pos != -1:
            flag = full_xor[pos:end_pos+1].decode('ascii', errors='ignore')
            print(f"Flag: {flag}")
        break

print("\n=== Analysis Complete ===")
print("Check the generated files and listen to them to find the hidden message.")
