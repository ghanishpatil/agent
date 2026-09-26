import wave
import numpy as np

audio_path = r"D:\mission-git-hackss\chall.wav"

print("=" * 60)
print("EXTRACTING ALL BIT PLANES")
print("=" * 60)

with wave.open(audio_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16)

print(f"Total samples: {len(samples)}")

# Check each bit position (0-15 for 16-bit audio)
for bit_pos in range(16):
    bit_values = (samples >> bit_pos) & 1
    
    # Extract bytes from this bit plane
    extracted_bytes = []
    for i in range(0, len(bit_values) - 7, 8):
        byte_val = 0
        for j in range(8):
            byte_val |= (bit_values[i + j] << j)
        extracted_bytes.append(byte_val)
    
    extracted_data = bytes(extracted_bytes)
    extracted_str = extracted_data.decode('latin-1', errors='ignore')
    
    # Look for flag
    if 'Kaal{' in extracted_str or 'kaal{' in extracted_str.lower():
        print(f"\n🎯 FLAG FOUND IN BIT PLANE {bit_pos}!")
        start = extracted_str.lower().find('kaal{')
        if start != -1:
            flag_section = extracted_str[start:start+100]
            print(f"Flag: {flag_section}")
            
            # Extract just the flag
            end = flag_section.find('}')
            if end != -1:
                flag = flag_section[:end+1]
                print(f"\n✓ EXTRACTED FLAG: {flag}")
    
    # Show first 100 chars for each bit plane
    if bit_pos <= 2:  # Show first few bit planes
        print(f"\nBit plane {bit_pos} (first 100 chars): {extracted_str[:100]}")

# Also check MSB (most significant bit)
print("\n" + "=" * 60)
print("CHECKING MSB (Bit 15)")
print("=" * 60)
msb_values = (samples >> 15) & 1
print(f"MSB 0s: {np.sum(msb_values == 0)}")
print(f"MSB 1s: {np.sum(msb_values == 1)}")

# Check for patterns in higher bits
print("\n" + "=" * 60)
print("BIT DISTRIBUTION")
print("=" * 60)
for bit_pos in range(16):
    bit_values = (samples >> bit_pos) & 1
    ones = np.sum(bit_values == 1)
    zeros = np.sum(bit_values == 0)
    ratio = ones / len(bit_values) * 100
    print(f"Bit {bit_pos:2d}: 1s={ones:5d} ({ratio:5.1f}%), 0s={zeros:5d}")
