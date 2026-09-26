import wave
import struct
import numpy as np

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Advanced Audio Steganography Analysis ===\n")

# Read audio
with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    sample_rate = wav.getframerate()
    n_channels = wav.getnchannels()

samples = np.frombuffer(frames, dtype=np.int16)
print(f"Total samples: {len(samples)}")
print(f"Sample rate: {sample_rate} Hz")
print(f"Duration: {len(samples) / sample_rate:.2f} seconds")

# 1. Check LSB of each byte (not just sample)
print("\n1. Extracting LSB from raw bytes...")
lsb_bits = []
for byte in frames:
    lsb_bits.append(byte & 1)

# Convert to bytes
lsb_bytes = []
for i in range(0, len(lsb_bits), 8):
    if i + 8 <= len(lsb_bits):
        byte_val = sum([lsb_bits[i+j] << j for j in range(8)])
        lsb_bytes.append(byte_val)

lsb_data = bytes(lsb_bytes)
print(f"Extracted {len(lsb_data)} bytes from LSB")

if b'Kaal{' in lsb_data:
    pos = lsb_data.find(b'Kaal{')
    end = lsb_data.find(b'}', pos)
    if end != -1:
        flag = lsb_data[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG FOUND: {flag}")
else:
    # Show first part
    print(f"First 200 bytes: {lsb_data[:200]}")

# 2. Try MSB extraction
print("\n2. Extracting MSB from raw bytes...")
msb_bits = []
for byte in frames:
    msb_bits.append((byte >> 7) & 1)

msb_bytes = []
for i in range(0, len(msb_bits), 8):
    if i + 8 <= len(msb_bits):
        byte_val = sum([msb_bits[i+j] << j for j in range(8)])
        msb_bytes.append(byte_val)

msb_data = bytes(msb_bytes)

if b'Kaal{' in msb_data:
    pos = msb_data.find(b'Kaal{')
    end = msb_data.find(b'}', pos)
    if end != -1:
        flag = msb_data[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG FOUND: {flag}")

# 3. Check for phase encoding
print("\n3. Analyzing phase relationships...")
# Simple phase check - look at sign changes
sign_changes = []
for i in range(len(samples)-1):
    if (samples[i] >= 0 and samples[i+1] < 0) or (samples[i] < 0 and samples[i+1] >= 0):
        sign_changes.append(1)
    else:
        sign_changes.append(0)

# Convert sign changes to bytes
sign_bytes = []
for i in range(0, len(sign_changes), 8):
    if i + 8 <= len(sign_changes):
        byte_val = sum([sign_changes[i+j] << j for j in range(8)])
        sign_bytes.append(byte_val)

sign_data = bytes(sign_bytes)

if b'Kaal{' in sign_data:
    pos = sign_data.find(b'Kaal{')
    end = sign_data.find(b'}', pos)
    if end != -1:
        flag = sign_data[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG FOUND: {flag}")

# 4. Check amplitude modulation
print("\n4. Checking amplitude patterns...")
# Group samples and check if amplitude encodes data
chunk_size = 100
amplitude_bits = []
for i in range(0, len(samples), chunk_size):
    chunk = samples[i:i+chunk_size]
    avg_amplitude = np.mean(np.abs(chunk))
    # Threshold to determine 0 or 1
    amplitude_bits.append(1 if avg_amplitude > 5000 else 0)

amp_bytes = []
for i in range(0, len(amplitude_bits), 8):
    if i + 8 <= len(amplitude_bits):
        byte_val = sum([amplitude_bits[i+j] << j for j in range(8)])
        amp_bytes.append(byte_val)

amp_data = bytes(amp_bytes)

if b'Kaal{' in amp_data:
    pos = amp_data.find(b'Kaal{')
    end = amp_data.find(b'}', pos)
    if end != -1:
        flag = amp_data[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG FOUND: {flag}")

# 5. Check for echo hiding
print("\n5. Analyzing echo patterns...")
# Look for repeated patterns that might encode data
delays = [10, 20, 50, 100, 200]
for delay in delays:
    correlation = []
    for i in range(len(samples) - delay):
        correlation.append(samples[i] * samples[i + delay])
    
    # Check if correlation pattern encodes data
    corr_bits = [1 if c > 0 else 0 for c in correlation[::100]]
    
    corr_bytes = []
    for i in range(0, len(corr_bits), 8):
        if i + 8 <= len(corr_bits):
            byte_val = sum([corr_bits[i+j] << j for j in range(8)])
            corr_bytes.append(byte_val)
    
    corr_data = bytes(corr_bytes)
    
    if b'Kaal{' in corr_data:
        pos = corr_data.find(b'Kaal{')
        end = corr_data.find(b'}', pos)
        if end != -1:
            flag = corr_data[pos:end+1].decode('ascii', errors='ignore')
            print(f"\n✓ FLAG FOUND with delay {delay}: {flag}")
            break

# 6. Try decoding as DTMF or similar
print("\n6. Checking for frequency-based encoding...")
# Simple frequency analysis - count zero crossings
zero_crossings = []
window = 100
for i in range(0, len(samples) - window, window):
    chunk = samples[i:i+window]
    crossings = sum([1 for j in range(len(chunk)-1) if chunk[j] * chunk[j+1] < 0])
    zero_crossings.append(crossings)

# Normalize to 0-255
if len(zero_crossings) > 0:
    max_cross = max(zero_crossings)
    if max_cross > 0:
        freq_bytes = bytes([int(c * 255 / max_cross) for c in zero_crossings])
        
        if b'Kaal{' in freq_bytes:
            pos = freq_bytes.find(b'Kaal{')
            end = freq_bytes.find(b'}', pos)
            if end != -1:
                flag = freq_bytes[pos:end+1].decode('ascii', errors='ignore')
                print(f"\n✓ FLAG FOUND: {flag}")

print("\n=== Analysis Complete ===")
