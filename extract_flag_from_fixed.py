import wave
import numpy as np

audio_path = r"D:\mission-git-hackss\chall.wav"

print("=" * 60)
print("EXTRACTING FLAG FROM FIXED AUDIO")
print("=" * 60)

with wave.open(audio_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16)

# Fix by shifting right 8 bits (moving upper byte to lower byte)
fixed_samples = samples >> 8

print(f"Fixed samples (first 20): {fixed_samples[:20]}")

# Extract LSB from fixed audio
lsb_bits = fixed_samples & 1
print(f"\nLSB distribution: 1s={np.sum(lsb_bits == 1)}, 0s={np.sum(lsb_bits == 0)}")

# Convert LSB bits to bytes
lsb_bytes = []
for i in range(0, len(lsb_bits) - 7, 8):
    byte_val = 0
    for j in range(8):
        byte_val |= (lsb_bits[i + j] << j)
    lsb_bytes.append(byte_val)

lsb_data = bytes(lsb_bytes)

# Try different encodings
for encoding in ['latin-1', 'utf-8', 'ascii']:
    try:
        lsb_str = lsb_data.decode(encoding, errors='ignore')
        print(f"\n{encoding.upper()} decoding (first 500 chars):")
        print(repr(lsb_str[:500]))
        
        # Look for flag pattern
        if 'Kaal{' in lsb_str:
            print(f"\n🎯 FLAG FOUND with {encoding}!")
            start = lsb_str.find('Kaal{')
            flag_section = lsb_str[start:start+100]
            end = flag_section.find('}')
            if end != -1:
                flag = flag_section[:end+1]
                print(f"✓ FLAG: {flag}")
        elif 'kaal{' in lsb_str.lower():
            print(f"\n🎯 FLAG FOUND (lowercase) with {encoding}!")
            start = lsb_str.lower().find('kaal{')
            flag_section = lsb_str[start:start+100]
            end = flag_section.find('}')
            if end != -1:
                flag = flag_section[:end+1]
                print(f"✓ FLAG: {flag}")
    except:
        pass

# Also search for any text that looks like flag format
print("\n" + "=" * 60)
print("SEARCHING FOR FLAG PATTERN")
print("=" * 60)

lsb_str = lsb_data.decode('latin-1', errors='ignore')

# Look for patterns like xx_xx_xx
import re
patterns = [
    r'Kaal\{[^}]+\}',
    r'kaal\{[^}]+\}',
    r'\{[a-zA-Z0-9_]+\}',
    r'[a-zA-Z]{2}_[a-zA-Z]{2}_[a-zA-Z]{2}',
]

for pattern in patterns:
    matches = re.findall(pattern, lsb_str, re.IGNORECASE)
    if matches:
        print(f"\nPattern '{pattern}' matches:")
        for match in matches[:10]:  # Show first 10 matches
            print(f"  {match}")

# Save the LSB data to a file for manual inspection
with open('lsb_extracted.txt', 'wb') as f:
    f.write(lsb_data)
print(f"\n✓ LSB data saved to: lsb_extracted.txt")

# Also try extracting from different bit positions of the fixed audio
print("\n" + "=" * 60)
print("CHECKING OTHER BIT POSITIONS IN FIXED AUDIO")
print("=" * 60)

for bit_pos in range(8):
    bit_values = (fixed_samples >> bit_pos) & 1
    
    extracted_bytes = []
    for i in range(0, len(bit_values) - 7, 8):
        byte_val = 0
        for j in range(8):
            byte_val |= (bit_values[i + j] << j)
        extracted_bytes.append(byte_val)
    
    extracted_data = bytes(extracted_bytes)
    extracted_str = extracted_data.decode('latin-1', errors='ignore')
    
    if 'Kaal{' in extracted_str or 'kaal{' in extracted_str.lower():
        print(f"\n🎯 FLAG FOUND IN BIT {bit_pos}!")
        start = max(0, extracted_str.lower().find('kaal{'))
        print(f"Context: {extracted_str[start:start+100]}")
