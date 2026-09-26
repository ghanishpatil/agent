import wave

audio_path = r"D:\mission-git-hackss\chall.wav"

# Based on the challenge:
# 1. The audio has a "mistake" - lower byte is all 0x00 ✓ FIXED
# 2. After fixing, there's "one small mistake" in the message
# 3. Flag format: Kaal{xx_xx_xx}

# The challenge title and description suggest:
# - "not as it should be" - audio is corrupted/shifted
# - "one small mistake remains" - after fixing, the flag has one wrong character

# Common CTF audio stego techniques:
# 1. LSB steganography - checked, nothing found
# 2. Spectral analysis - would need to visualize
# 3. Metadata - let's check
# 4. Spoken message - need to listen/transcribe

print("=" * 60)
print("FINAL ANALYSIS")
print("=" * 60)

# Check if there's any text in the WAV metadata
with open(audio_path, 'rb') as f:
    data = f.read()
    
# Look for common metadata markers
markers = [b'INAM', b'IART', b'ICMT', b'ICOP', b'ICRD', b'ISFT']
for marker in markers:
    if marker in data:
        idx = data.find(marker)
        # Metadata usually follows the marker
        metadata = data[idx:idx+100]
        print(f"\nFound {marker}: {metadata}")

# Check LIST chunk more carefully
if b'LIST' in data:
    idx = data.find(b'LIST')
    list_chunk = data[idx:idx+200]
    print(f"\nLIST chunk: {list_chunk}")
    print(f"As text: {list_chunk.decode('latin-1', errors='ignore')}")

# Based on typical CTF patterns, if the flag isn't in the data,
# it's likely spoken in the audio. The "one small mistake" could be:
# - One letter is wrong (e.g., "Laal" instead of "Kaal")
# - One character in the flag content is wrong

print("\n" + "=" * 60)
print("HYPOTHESIS")
print("=" * 60)
print("The audio likely contains a SPOKEN message.")
print("After fixing the byte shift, you need to:")
print("1. Play 'chall_properly_fixed.wav'")
print("2. Listen for a spoken flag")
print("3. The spoken flag will have 'one small mistake'")
print("4. Correct that mistake to get the real flag")
print("\nFor example, if you hear 'Kaal{ab_cd_ef}' but one")
print("letter sounds wrong, try variations like:")
print("- Kaal{ab_cd_ef} -> Kaal{ab_cd_eg}")
print("- Or the first letter: Laal{ab_cd_ef} -> Kaal{ab_cd_ef}")

# Let me also try to see if there's a simple pattern
# Maybe the flag is just the filename or something obvious?
print("\n" + "=" * 60)
print("CHECKING FOR OBVIOUS PATTERNS")
print("=" * 60)

# Common CTF flag patterns
test_flags = [
    "Kaal{au_di_o}",  # audio
    "Kaal{wa_ve_s}",  # waves
    "Kaal{st_eg_o}",  # stego
    "Kaal{by_te_s}",  # bytes
    "Kaal{fi_xe_d}",  # fixed
    "Kaal{sh_if_t}",  # shift
]

print("Common patterns to try:")
for flag in test_flags:
    print(f"  {flag}")

print("\n" + "=" * 60)
print("NEXT STEPS")
print("=" * 60)
print("1. Play the fixed audio file: chall_properly_fixed.wav")
print("2. Use speech recognition if available")
print("3. Or manually transcribe what you hear")
print("4. Look for the 'one small mistake' and fix it")
