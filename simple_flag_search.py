import wave
import struct

audio_path = r"D:\mission-git-hackss\chall.wav"

# Read raw file
with open(audio_path, 'rb') as f:
    all_data = f.read()

# Find data chunk
data_pos = all_data.find(b'data')
audio_start = data_pos + 8

# Extract non-zero bytes
non_zero = bytes([all_data[i] for i in range(audio_start + 1, len(all_data), 2)])

print("=" * 60)
print("SIMPLE DIRECT SEARCH")
print("=" * 60)

# Search for "Kaal" with different cases and nearby characters
search_terms = [
    b'Kaal{',
    b'kaal{',
    b'KAAL{',
    b'Laal{',  # L instead of K (one letter off)
    b'Jaal{',  # J instead of K
    b'Maal{',  # M instead of K
    b'Iaal{',  # I instead of K
    b'Kaal[',  # [ instead of {
    b'Kaal(',  # ( instead of {
]

for term in search_terms:
    if term in non_zero:
        idx = non_zero.find(term)
        print(f"\n🎯 FOUND: {term}")
        print(f"Position: {idx}")
        context = non_zero[idx:idx+50]
        print(f"Context: {context}")
        print(f"As text: {context.decode('latin-1', errors='ignore')}")

# Also search for just "aal{" to catch any first letter
if b'aal{' in non_zero:
    idx = 0
    while True:
        idx = non_zero.find(b'aal{', idx)
        if idx == -1:
            break
        
        # Get the character before
        if idx > 0:
            before_char = chr(non_zero[idx-1])
            context = non_zero[max(0, idx-5):idx+20]
            print(f"\nFound 'aal{{' at {idx}, preceded by '{before_char}'")
            print(f"Context: {context.decode('latin-1', errors='ignore')}")
        
        idx += 1

# Search for underscore patterns (xx_xx_xx)
import re
text = non_zero.decode('latin-1', errors='ignore')
pattern = re.compile(r'[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}')
matches = pattern.findall(text)
if matches:
    print(f"\n" + "=" * 60)
    print(f"FOUND {len(matches)} UNDERSCORE PATTERNS:")
    print("=" * 60)
    for match in matches[:10]:
        idx = text.find(match)
        context = text[max(0, idx-15):idx+len(match)+5]
        print(f"\n{match}")
        print(f"Context: {repr(context)}")

# Final attempt: maybe the flag is at a specific location
# Check the beginning and end of the audio data
print("\n" + "=" * 60)
print("CHECKING BEGINNING AND END")
print("=" * 60)

print(f"First 200 bytes:")
print(non_zero[:200])
print(f"\nAs text: {non_zero[:200].decode('latin-1', errors='ignore')}")

print(f"\nLast 200 bytes:")
print(non_zero[-200:])
print(f"\nAs text: {non_zero[-200:].decode('latin-1', errors='ignore')}")
