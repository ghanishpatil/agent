import struct

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Detailed WAV Header Analysis ===\n")

with open(wav_path, 'rb') as f:
    data = bytearray(f.read())

# Parse RIFF header
riff_id = data[0:4]
file_size = struct.unpack('<I', data[4:8])[0]
wave_id = data[8:12]

print(f"RIFF ID: {riff_id} (should be b'RIFF')")
print(f"File size in header: {file_size + 8}")
print(f"Actual file size: {len(data)}")
print(f"WAVE ID: {wave_id} (should be b'WAVE')")

# Check if WAVE is corrupted
if wave_id != b'WAVE':
    print(f"\n! WAVE marker is corrupted: {wave_id}")
    print(f"  Hex: {wave_id.hex()}")
    
    # Common corruption: single character off
    if wave_id == b'WAVA' or wave_id == b'WAVF':
        print("  Fixing WAVE marker...")
        data[8:12] = b'WAVE'
        
# Parse fmt chunk
fmt_pos = 12
fmt_id = data[fmt_pos:fmt_pos+4]
fmt_size = struct.unpack('<I', data[fmt_pos+4:fmt_pos+8])[0]

print(f"\nfmt ID: {fmt_id} (should be b'fmt ')")
print(f"fmt size: {fmt_size}")

if fmt_id != b'fmt ':
    print(f"! fmt marker is corrupted: {fmt_id}")
    print(f"  Hex: {fmt_id.hex()}")

# Parse fmt data
audio_format = struct.unpack('<H', data[fmt_pos+8:fmt_pos+10])[0]
num_channels = struct.unpack('<H', data[fmt_pos+10:fmt_pos+12])[0]
sample_rate = struct.unpack('<I', data[fmt_pos+12:fmt_pos+16])[0]
byte_rate = struct.unpack('<I', data[fmt_pos+16:fmt_pos+20])[0]
block_align = struct.unpack('<H', data[fmt_pos+20:fmt_pos+22])[0]
bits_per_sample = struct.unpack('<H', data[fmt_pos+22:fmt_pos+24])[0]

print(f"\nAudio format: {audio_format}")
print(f"Channels: {num_channels}")
print(f"Sample rate: {sample_rate}")
print(f"Byte rate: {byte_rate}")
print(f"Block align: {block_align}")
print(f"Bits per sample: {bits_per_sample}")

# Calculate expected values
expected_byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
expected_block_align = num_channels * (bits_per_sample // 8)

print(f"\nExpected byte rate: {expected_byte_rate}")
print(f"Expected block align: {expected_block_align}")

if byte_rate != expected_byte_rate:
    print(f"! Byte rate mismatch - fixing...")
    data[fmt_pos+16:fmt_pos+20] = struct.pack('<I', expected_byte_rate)
    
if block_align != expected_block_align:
    print(f"! Block align mismatch - fixing...")
    data[fmt_pos+20:fmt_pos+22] = struct.pack('<H', expected_block_align)

# Find and check data chunk
data_pos = data.find(b'data')
if data_pos != -1:
    data_id = data[data_pos:data_pos+4]
    data_size = struct.unpack('<I', data[data_pos+4:data_pos+8])[0]
    
    print(f"\ndata ID: {data_id} (should be b'data')")
    print(f"data size in header: {data_size}")
    
    actual_data_size = len(data) - data_pos - 8
    print(f"Actual data size: {actual_data_size}")
    
    if data_size != actual_data_size:
        print(f"! Data size mismatch - fixing...")
        data[data_pos+4:data_pos+8] = struct.pack('<I', actual_data_size)
        
        # Also update RIFF file size
        new_file_size = len(data) - 8
        data[4:8] = struct.pack('<I', new_file_size)

# Check for common single-byte errors
print("\n=== Checking for Single-Byte Corruption ===")

# Look for almost-correct markers
for i in range(len(data) - 4):
    chunk = data[i:i+4]
    
    # Check if it's one byte off from 'Kaal'
    if chunk[0:3] == b'Kaa' or chunk[1:4] == b'aal':
        print(f"Found near-match to 'Kaal' at position {i}: {chunk}")
        
    # Check for 'laaK' (reversed)
    if chunk == b'laaK':
        print(f"Found reversed 'Kaal' at position {i}")
        # Look for the rest of the flag
        flag_area = data[i:i+50]
        print(f"Area: {flag_area}")
        # Reverse it
        reversed_flag = flag_area[::-1]
        print(f"Reversed: {reversed_flag}")

# Save corrected file
output_path = 'chall_fixed.wav'
with open(output_path, 'wb') as f:
    f.write(data)
print(f"\n✓ Saved corrected WAV to {output_path}")

# Try to extract text from the corrected file
print("\n=== Searching for Flag in Corrected File ===")
if b'Kaal{' in data:
    pos = data.find(b'Kaal{')
    print(f"✓ Found 'Kaal{{' at position {pos}")
    end_pos = data.find(b'}', pos)
    if end_pos != -1:
        flag = data[pos:end_pos+1].decode('ascii', errors='ignore')
        print(f"\nFLAG: {flag}")
    else:
        print(f"Flag area: {data[pos:pos+100]}")
