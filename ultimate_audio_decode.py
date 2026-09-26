import wave
import struct

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Ultimate Audio Decode ===\n")

# Read raw bytes
with open(wav_path, 'rb') as f:
    raw_data = f.read()

# Read as wave
with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())

samples = struct.unpack(f'<{len(frames)//2}h', frames)

print(f"Total samples: {len(samples)}")
print(f"Frame data length: {len(frames)} bytes")

# The challenge says "one small mistake" - let's check if bytes are swapped
print("\n1. Checking if low/high bytes encode different messages...")

# Extract low bytes
low_bytes = bytes([s & 0xFF for s in samples])
print(f"Low bytes first 100: {low_bytes[:100]}")

if b'Kaal{' in low_bytes:
    pos = low_bytes.find(b'Kaal{')
    end = low_bytes.find(b'}', pos)
    if end != -1:
        flag = low_bytes[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG IN LOW BYTES: {flag}")

# Extract high bytes
high_bytes = bytes([(s >> 8) & 0xFF for s in samples])
print(f"\nHigh bytes first 100: {high_bytes[:100]}")

if b'Kaal{' in high_bytes:
    pos = high_bytes.find(b'Kaal{')
    end = high_bytes.find(b'}', pos)
    if end != -1:
        flag = high_bytes[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG IN HIGH BYTES: {flag}")

# Maybe the "mistake" is that high and low bytes are swapped
print("\n2. Checking if bytes need to be swapped...")
swapped_bytes = bytes([(s >> 8) & 0xFF for s in samples] + [s & 0xFF for s in samples])

if b'Kaal{' in swapped_bytes:
    pos = swapped_bytes.find(b'Kaal{')
    end = swapped_bytes.find(b'}', pos)
    if end != -1:
        flag = swapped_bytes[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG IN SWAPPED BYTES: {flag}")

# Try interleaving differently
print("\n3. Checking different byte arrangements...")
# Alternate between high and low
alternating = []
for s in samples:
    alternating.append((s >> 8) & 0xFF)
    alternating.append(s & 0xFF)
alternating_bytes = bytes(alternating)

if b'Kaal{' in alternating_bytes:
    pos = alternating_bytes.find(b'Kaal{')
    end = alternating_bytes.find(b'}', pos)
    if end != -1:
        flag = alternating_bytes[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG IN ALTERNATING BYTES: {flag}")

# Check if we need to reverse the byte order within each sample
print("\n4. Checking reversed byte order...")
reversed_samples = []
for i in range(0, len(frames), 2):
    # Swap the two bytes of each sample
    reversed_samples.append(frames[i+1])
    reversed_samples.append(frames[i])
reversed_bytes = bytes(reversed_samples)

if b'Kaal{' in reversed_bytes:
    pos = reversed_bytes.find(b'Kaal{')
    end = reversed_bytes.find(b'}', pos)
    if end != -1:
        flag = reversed_bytes[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG IN REVERSED BYTES: {flag}")

# Check if the flag is in the raw frames but with one character wrong
print("\n5. Searching for near-matches to 'Kaal{'...")
# Look for patterns like "Kaal[", "Kaal}", "Kaai{", etc.
for i in range(len(frames) - 10):
    chunk = frames[i:i+10]
    # Check if it's close to "Kaal{"
    if chunk[0:4] == b'Kaal' or chunk[0:4] == b'Kaai' or chunk[0:4] == b'Kaal':
        print(f"Found near-match at {i}: {chunk}")

# Try reading the entire file as text with error handling
print("\n6. Extracting all printable ASCII from file...")
printable_chars = []
for byte in raw_data:
    if 32 <= byte <= 126:
        printable_chars.append(chr(byte))
    elif byte == 10 or byte == 13:  # newline/carriage return
        printable_chars.append('\n')

printable_text = ''.join(printable_chars)
print(f"Printable text ({len(printable_text)} chars):")
print(printable_text)

if 'Kaal{' in printable_text:
    pos = printable_text.find('Kaal{')
    end = printable_text.find('}', pos)
    if end != -1:
        flag = printable_text[pos:end+1]
        print(f"\n✓ FLAG FOUND: {flag}")

# Check for common steganography patterns
print("\n7. Checking for DeepSound/OpenPuff patterns...")
# These tools often leave markers
markers = [b'DPSM', b'OPUF', b'STEG', b'HIDE']
for marker in markers:
    if marker in raw_data:
        pos = raw_data.find(marker)
        print(f"Found {marker} at position {pos}")
        context = raw_data[pos:pos+200]
        print(f"Context: {context}")

print("\n=== Decode Complete ===")
