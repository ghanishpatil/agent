import wave
import numpy as np
import struct

audio_path = r"D:\mission-git-hackss\chall.wav"

# Read as raw bytes
with open(audio_path, 'rb') as f:
    all_data = f.read()

# Find data chunk
data_pos = all_data.find(b'data')
data_size = struct.unpack('<I', all_data[data_pos+4:data_pos+8])[0]
audio_start = data_pos + 8

print("=" * 60)
print("EXTRACTING TEXT FROM AUDIO")
print("=" * 60)

# The audio is 16-bit little-endian samples
# Each sample is [LSB, MSB] where LSB=0x00 and MSB=data
# So bytes are: 00 FF, 00 02, 00 10, etc.

# Extract just the non-zero bytes (every other byte starting from position 1)
non_zero_bytes = []
for i in range(audio_start + 1, audio_start + data_size, 2):
    non_zero_bytes.append(all_data[i])

message_bytes = bytes(non_zero_bytes)

print(f"Extracted {len(message_bytes)} bytes")
print(f"\nFirst 500 bytes as hex:")
print(message_bytes[:500].hex())

print(f"\nFirst 500 bytes as ASCII (printable only):")
printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in message_bytes[:500])
print(printable)

# Look for flag pattern
print("\n" + "=" * 60)
print("SEARCHING FOR FLAG")
print("=" * 60)

# Search for Kaal{ or similar
if b'Kaal{' in message_bytes:
    idx = message_bytes.find(b'Kaal{')
    print(f"Found 'Kaal{{' at position {idx}!")
    print(f"Flag: {message_bytes[idx:idx+50]}")
elif b'kaal{' in message_bytes.lower():
    idx = message_bytes.lower().find(b'kaal{')
    print(f"Found 'kaal{{' at position {idx}!")
    print(f"Flag: {message_bytes[idx:idx+50]}")

# Try to decode as text
try:
    text = message_bytes.decode('latin-1', errors='ignore')
    print(f"\nFull text (first 1000 chars):")
    print(text[:1000])
    
    # Look for flag in text
    if 'Kaal{' in text or 'kaal{' in text.lower():
        start = text.lower().find('kaal{')
        if start != -1:
            print(f"\n🎯 FLAG FOUND IN TEXT!")
            print(f"Flag section: {text[start:start+100]}")
            
            # Extract just the flag
            end = text.find('}', start)
            if end != -1:
                flag = text[start:end+1]
                print(f"\n✓ EXTRACTED FLAG: {flag}")
                
                # Check if it matches the format xx_xx_xx
                import re
                if re.match(r'[Kk]aal\{[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}\}', flag):
                    print("✓ Flag matches expected format!")
                else:
                    print("⚠️  Flag doesn't match expected format - might have a mistake!")
except:
    pass

# Also check for common substitutions (the "one small mistake")
print("\n" + "=" * 60)
print("CHECKING FOR COMMON MISTAKES")
print("=" * 60)

# Maybe K is replaced with L, J, M, etc.
substitutions = {
    'K': ['L', 'J', 'M', 'I'],
    'a': ['e', 'o', 'i'],
    '_': ['-', '.', ' '],
}

for original, replacements in substitutions.items():
    for replacement in replacements:
        pattern = f"{replacement}aal{{".encode()
        if pattern in message_bytes:
            idx = message_bytes.find(pattern)
            print(f"Found '{replacement}aal{{' at position {idx}!")
            print(f"Context: {message_bytes[idx:idx+50]}")

# Save the extracted message
with open('extracted_message.txt', 'wb') as f:
    f.write(message_bytes)
print(f"\n✓ Message saved to: extracted_message.txt")
