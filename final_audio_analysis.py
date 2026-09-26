import wave
import numpy as np

audio_path = r"D:\mission-git-hackss\chall.wav"

print("=" * 60)
print("FINAL COMPREHENSIVE ANALYSIS")
print("=" * 60)

with wave.open(audio_path, 'rb') as wav:
    params = wav.getparams()
    frames = wav.readframes(wav.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16)

print(f"Original samples: {len(samples)}")
print(f"Duration: {len(samples) / 8000:.2f} seconds")

# The issue: lower byte is all 0x00
# Fix: shift right by 8 to get actual 8-bit audio values
fixed_samples = samples >> 8

# But we need to expand back to 16-bit for proper playback
# Scale the 8-bit values to 16-bit range
fixed_samples_16bit = fixed_samples.astype(np.int16) * 256

# Save the fixed audio
with wave.open('chall_properly_fixed.wav', 'wb') as wav_out:
    wav_out.setparams(params)
    wav_out.writeframes(fixed_samples_16bit.tobytes())

print("✓ Fixed audio saved to: chall_properly_fixed.wav")
print("  You can now play this file to hear the message!")

# Also try to extract any text that might be encoded
print("\n" + "=" * 60)
print("CHECKING FOR ENCODED TEXT")
print("=" * 60)

# Method: Check if the 8-bit values spell out ASCII
fixed_8bit = fixed_samples.astype(np.int8)
print(f"8-bit values (first 100): {fixed_8bit[:100]}")

# Try to interpret as ASCII
ascii_attempt = bytes([int(b) & 0xFF for b in fixed_8bit if 0 <= int(b) < 128])
print(f"\nASCII interpretation (first 200 chars):")
print(ascii_attempt[:200])

# Check for flag
if b'Kaal{' in ascii_attempt or b'kaal{' in ascii_attempt.lower():
    print("\n🎯 FLAG FOUND!")
    start = ascii_attempt.lower().find(b'kaal{')
    if start != -1:
        print(ascii_attempt[start:start+50])

# Try unsigned interpretation
unsigned_8bit = (samples >> 8) & 0xFF
unsigned_bytes = bytes(unsigned_8bit)

print(f"\nUnsigned 8-bit (first 200 bytes):")
print(unsigned_bytes[:200])

# Look for patterns that might be a flag with a "mistake"
# Flag format is Kaal{xx_xx_xx}
# Maybe it's encoded as Laal or Jaal or Kaal with wrong characters?

print("\n" + "=" * 60)
print("SEARCHING FOR NEAR-MISS FLAGS")
print("=" * 60)

# Search for similar patterns
patterns = [
    b'Kaal{', b'kaal{', b'KAAL{',
    b'Laal{', b'laal{', b'LAAL{',
    b'Jaal{', b'jaal{', b'JAAL{',
    b'Maal{', b'maal{', b'MAAL{',
    b'Kaal[', b'Kaal(', b'Kaal<',
]

for pattern in patterns:
    if pattern in unsigned_bytes:
        idx = unsigned_bytes.find(pattern)
        print(f"Found {pattern} at position {idx}")
        print(f"Context: {unsigned_bytes[idx:idx+50]}")

# Also check if maybe the flag is there but with bit errors
# Try flipping individual bits
print("\n" + "=" * 60)
print("TRYING BIT FLIPS")
print("=" * 60)

# K = 0x4B, if one bit is wrong:
# 0x4A (J), 0x49 (I), 0x4F (O), 0x43 (C), 0x5B ([), 0x6B (k), etc.

for bit_flip in range(8):
    flipped = bytes([b ^ (1 << bit_flip) for b in unsigned_8bit])
    if b'Kaal{' in flipped:
        print(f"\n🎯 FOUND WITH BIT {bit_flip} FLIPPED!")
        start = flipped.find(b'Kaal{')
        print(f"Flag: {flipped[start:start+50]}")

# Check the actual hex values around common letters
print("\n" + "=" * 60)
print("HEX DUMP OF INTERESTING SECTIONS")
print("=" * 60)

# Look for sequences that might be flag-like
for i in range(0, len(unsigned_bytes) - 20, 100):
    section = unsigned_bytes[i:i+20]
    # Check if it has curly braces or underscores
    if b'{' in section or b'}' in section or b'_' in section:
        print(f"\nPosition {i}: {section.hex()} = {section}")

# Final attempt: maybe the "mistake" is in the flag itself
# Like Kaal{ab_cd_ef} but one character is wrong
print("\n" + "=" * 60)
print("MANUAL INSPECTION HINTS")
print("=" * 60)
print("The challenge says 'one small mistake remains' AFTER uncovering.")
print("This suggests:")
print("1. First, fix the audio (shift right 8 bits) ✓")
print("2. Then, listen to it or extract the message")
print("3. The extracted message will have 'one small mistake'")
print("4. Fix that mistake to get the real flag")
print("\nNext steps:")
print("- Play 'chall_properly_fixed.wav' to hear the message")
print("- Or use speech recognition to extract text")
print("- Look for a flag with one wrong character")
