import wave
import struct

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== LSB Extraction from Audio ===\n")

with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    
# Convert to 16-bit samples
samples = struct.unpack(f'<{len(frames)//2}h', frames)

print(f"Total samples: {len(samples)}")

# Extract LSB from each sample
lsb_bits = []
for sample in samples:
    # Get the least significant bit
    lsb_bits.append(sample & 1)

print(f"Extracted {len(lsb_bits)} LSB bits")

# Convert bits to bytes
lsb_bytes = []
for i in range(0, len(lsb_bits), 8):
    if i + 8 <= len(lsb_bits):
        byte_bits = lsb_bits[i:i+8]
        byte_val = 0
        for j, bit in enumerate(byte_bits):
            byte_val |= (bit << j)
        lsb_bytes.append(byte_val)

lsb_data = bytes(lsb_bytes)

print(f"\nFirst 500 bytes of LSB data:")
print(lsb_data[:500])

# Search for flag
if b'Kaal{' in lsb_data:
    pos = lsb_data.find(b'Kaal{')
    print(f"\n✓ Found flag at position {pos}!")
    end_pos = lsb_data.find(b'}', pos)
    if end_pos != -1:
        flag = lsb_data[pos:end_pos+1].decode('ascii', errors='ignore')
        print(f"Flag: {flag}")
    else:
        print(f"Flag start: {lsb_data[pos:pos+50]}")
else:
    print("\n✗ No flag found in LSB data")
    
# Try reversed LSB
print("\n=== Trying Reversed Bit Order ===")
lsb_bytes_rev = []
for i in range(0, len(lsb_bits), 8):
    if i + 8 <= len(lsb_bits):
        byte_bits = lsb_bits[i:i+8]
        byte_val = 0
        for j, bit in enumerate(byte_bits):
            byte_val |= (bit << (7-j))  # Reverse bit order
        lsb_bytes_rev.append(byte_val)

lsb_data_rev = bytes(lsb_bytes_rev)

if b'Kaal{' in lsb_data_rev:
    pos = lsb_data_rev.find(b'Kaal{')
    print(f"\n✓ Found flag at position {pos}!")
    end_pos = lsb_data_rev.find(b'}', pos)
    if end_pos != -1:
        flag = lsb_data_rev[pos:end_pos+1].decode('ascii', errors='ignore')
        print(f"Flag: {flag}")
    else:
        print(f"Flag start: {lsb_data_rev[pos:pos+50]}")

# Try MSB (most significant bit)
print("\n=== Trying MSB Extraction ===")
msb_bits = []
for sample in samples:
    # Get the most significant bit of the lower byte
    msb_bits.append((sample >> 7) & 1)

msb_bytes = []
for i in range(0, len(msb_bits), 8):
    if i + 8 <= len(msb_bits):
        byte_bits = msb_bits[i:i+8]
        byte_val = 0
        for j, bit in enumerate(byte_bits):
            byte_val |= (bit << j)
        msb_bytes.append(byte_val)

msb_data = bytes(msb_bytes)

if b'Kaal{' in msb_data:
    pos = msb_data.find(b'Kaal{')
    print(f"\n✓ Found flag at position {pos}!")
    end_pos = msb_data.find(b'}', pos)
    if end_pos != -1:
        flag = msb_data[pos:end_pos+1].decode('ascii', errors='ignore')
        print(f"Flag: {flag}")

# Save LSB data for inspection
with open('lsb_extracted.bin', 'wb') as f:
    f.write(lsb_data)
print("\n✓ Saved LSB data to lsb_extracted.bin")
