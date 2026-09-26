import wave
import numpy as np

audio_path = r"D:\mission-git-hackss\chall.wav"

print("=" * 60)
print("FIXING BYTE-SHIFTED AUDIO")
print("=" * 60)

with wave.open(audio_path, 'rb') as wav:
    params = wav.getparams()
    frames = wav.readframes(wav.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16)

print(f"Original samples (first 20): {samples[:20]}")
print(f"Original hex (first 10): {[hex(int(s) & 0xFFFF) for s in samples[:10]]}")

# The lower 8 bits are all 0, so the data must be in the upper byte
# This means samples are shifted left by 8 bits
# To fix: shift right by 8 bits

# Method 1: Shift right by 8 bits
fixed_samples_shift = samples >> 8
print(f"\nShifted right by 8 (first 20): {fixed_samples_shift[:20]}")

# Method 2: Extract upper byte and treat as signed 8-bit, then expand to 16-bit
upper_bytes = (samples >> 8) & 0xFF
# Convert to signed 8-bit
signed_bytes = np.array([b if b < 128 else b - 256 for b in upper_bytes], dtype=np.int16)
# Scale up to 16-bit range
fixed_samples_byte = signed_bytes * 256

print(f"Upper byte method (first 20): {fixed_samples_byte[:20]}")

# Save both versions
for method, fixed_samples, filename in [
    ("shift", fixed_samples_shift, "chall_fixed_shift.wav"),
    ("byte", fixed_samples_byte, "chall_fixed_byte.wav")
]:
    with wave.open(filename, 'wb') as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(fixed_samples.astype(np.int16).tobytes())
    print(f"\n✓ Saved {method} method to: {filename}")

# Now check for LSB steganography in the FIXED audio
print("\n" + "=" * 60)
print("CHECKING LSB IN FIXED AUDIO")
print("=" * 60)

for method, fixed_samples, filename in [
    ("shift", fixed_samples_shift, "chall_fixed_shift.wav"),
    ("byte", fixed_samples_byte, "chall_fixed_byte.wav")
]:
    print(f"\n{method.upper()} METHOD:")
    
    # Extract LSB
    lsb_bits = fixed_samples & 1
    lsb_bytes = []
    for i in range(0, len(lsb_bits) - 7, 8):
        byte_val = 0
        for j in range(8):
            byte_val |= (lsb_bits[i + j] << j)
        lsb_bytes.append(byte_val)
    
    lsb_data = bytes(lsb_bytes)
    lsb_str = lsb_data.decode('latin-1', errors='ignore')
    
    print(f"LSB data (first 200 chars): {lsb_str[:200]}")
    
    if 'Kaal{' in lsb_str or 'kaal{' in lsb_str.lower():
        print(f"\n🎯 FLAG FOUND!")
        start = lsb_str.lower().find('kaal{')
        if start != -1:
            flag_section = lsb_str[start:start+100]
            end = flag_section.find('}')
            if end != -1:
                flag = flag_section[:end+1]
                print(f"✓ FLAG: {flag}")

# Also check if the ORIGINAL lower byte (which is all 0s) might contain hidden data
# when we look at it differently
print("\n" + "=" * 60)
print("CHECKING IF LOWER BYTE NEEDS TO BE POPULATED")
print("=" * 60)

# Maybe the lower byte should be extracted from somewhere else?
# Let's check the raw file for any patterns
with open(audio_path, 'rb') as f:
    all_data = f.read()
    
print(f"File size: {len(all_data)} bytes")
print(f"Expected audio data size: {len(samples) * 2} bytes")

# Check if there's extra data at the end
header_size = len(all_data) - (len(samples) * 2)
print(f"Header/metadata size: {header_size} bytes")

if len(all_data) > len(samples) * 2 + 100:
    extra_data = all_data[len(samples) * 2 + 100:]
    print(f"\nExtra data at end: {len(extra_data)} bytes")
    print(f"First 200 bytes: {extra_data[:200]}")
    
    extra_str = extra_data.decode('latin-1', errors='ignore')
    if 'Kaal{' in extra_str or 'kaal{' in extra_str.lower():
        print(f"\n🎯 FLAG IN EXTRA DATA!")
        start = extra_str.lower().find('kaal{')
        if start != -1:
            print(extra_str[start:start+50])
