import wave
import struct
import re

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Exhaustive Flag Search ===\n")

# Read entire file as bytes
with open(wav_path, 'rb') as f:
    file_data = f.read()

print(f"File size: {len(file_data)} bytes\n")

# Search for various flag patterns
patterns = [
    b'Kaal{',
    b'laaK{',  # Reversed
    b'Kaal}',  # Wrong bracket
    b'Kaal[',  # Wrong bracket
    b'Kaal(',  # Wrong bracket
    b'Kaai{',  # Typo
    b'Kaal',   # Just the prefix
    b'flag{',
    b'FLAG{',
]

print("1. Searching for flag patterns in raw file...")
for pattern in patterns:
    if pattern in file_data:
        pos = file_data.find(pattern)
        print(f"✓ Found '{pattern.decode('ascii', errors='ignore')}' at position {pos}")
        context = file_data[max(0, pos-20):pos+100]
        print(f"  Context: {context}")
        print(f"  Hex: {context.hex()}")
        print()

# Read audio samples
with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())

samples = struct.unpack(f'<{len(frames)//2}h', frames)

# Try different encodings
print("\n2. Trying different sample interpretations...")

# A. Absolute value of samples
abs_samples = [abs(s) for s in samples]
abs_bytes = bytes([s & 0xFF for s in abs_samples])
if b'Kaal{' in abs_bytes:
    pos = abs_bytes.find(b'Kaal{')
    print(f"✓ Found in absolute values at {pos}")
    end = abs_bytes.find(b'}', pos)
    if end != -1:
        print(f"FLAG: {abs_bytes[pos:end+1].decode('ascii', errors='ignore')}")

# B. Signed to unsigned conversion
unsigned_samples = [(s + 32768) & 0xFFFF for s in samples]
unsigned_bytes = bytes([s & 0xFF for s in unsigned_samples])
if b'Kaal{' in unsigned_bytes:
    pos = unsigned_bytes.find(b'Kaal{')
    print(f"✓ Found in unsigned conversion at {pos}")
    end = unsigned_bytes.find(b'}', pos)
    if end != -1:
        print(f"FLAG: {unsigned_bytes[pos:end+1].decode('ascii', errors='ignore')}")

# C. Take every other sample
even_samples = samples[::2]
even_bytes = bytes([s & 0xFF for s in even_samples])
if b'Kaal{' in even_bytes:
    pos = even_bytes.find(b'Kaal{')
    print(f"✓ Found in even samples at {pos}")
    end = even_bytes.find(b'}', pos)
    if end != -1:
        print(f"FLAG: {even_bytes[pos:end+1].decode('ascii', errors='ignore')}")

odd_samples = samples[1::2]
odd_bytes = bytes([s & 0xFF for s in odd_samples])
if b'Kaal{' in odd_bytes:
    pos = odd_bytes.find(b'Kaal{')
    print(f"✓ Found in odd samples at {pos}")
    end = odd_bytes.find(b'}', pos)
    if end != -1:
        print(f"FLAG: {odd_bytes[pos:end+1].decode('ascii', errors='ignore')}")

# D. Difference between consecutive samples
print("\n3. Checking sample differences...")
diffs = [samples[i+1] - samples[i] for i in range(len(samples)-1)]
diff_bytes = bytes([(d & 0xFF) for d in diffs])
if b'Kaal{' in diff_bytes:
    pos = diff_bytes.find(b'Kaal{')
    print(f"✓ Found in differences at {pos}")
    end = diff_bytes.find(b'}', pos)
    if end != -1:
        print(f"FLAG: {diff_bytes[pos:end+1].decode('ascii', errors='ignore')}")

# E. Check for ROT13 or Caesar cipher
print("\n4. Checking for character substitution...")
# Extract printable characters from high byte
high_bytes = bytes([(s >> 8) & 0xFF for s in samples])
printable = ''.join([chr(b) if 32 <= b <= 126 else '' for b in high_bytes])

# Try ROT13
rot13_trans = str.maketrans(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
)
rot13_text = printable.translate(rot13_trans)
if 'Kaal{' in rot13_text:
    pos = rot13_text.find('Kaal{')
    end = rot13_text.find('}', pos)
    if end != -1:
        print(f"✓ Found with ROT13!")
        print(f"FLAG: {rot13_text[pos:end+1]}")

# Try Caesar shifts
for shift in range(1, 26):
    shifted = ''
    for char in printable:
        if 'A' <= char <= 'Z':
            shifted += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
        elif 'a' <= char <= 'z':
            shifted += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
        else:
            shifted += char
    
    if 'Kaal{' in shifted:
        pos = shifted.find('Kaal{')
        end = shifted.find('}', pos)
        if end != -1:
            print(f"✓ Found with Caesar shift {shift}!")
            print(f"FLAG: {shifted[pos:end+1]}")
            break

# F. Check metadata and comments
print("\n5. Checking all text strings in file...")
text_strings = re.findall(b'[\x20-\x7E]{10,}', file_data)
for i, string in enumerate(text_strings):
    print(f"String {i}: {string.decode('ascii', errors='ignore')}")
    if b'Kaal' in string or b'flag' in string.lower():
        print(f"  *** Potential flag! ***")

print("\n=== Search Complete ===")
