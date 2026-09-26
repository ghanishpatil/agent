import wave
import numpy as np
import re

audio_path = r"D:\mission-git-hackss\chall.wav"

with open(audio_path, 'rb') as f:
    all_data = f.read()

# Find data chunk
data_pos = all_data.find(b'data')
audio_start = data_pos + 8

# Extract non-zero bytes (every other byte)
non_zero_bytes = []
for i in range(audio_start + 1, len(all_data), 2):
    non_zero_bytes.append(all_data[i])

message_bytes = bytes(non_zero_bytes)
message_text = message_bytes.decode('latin-1', errors='ignore')

print("=" * 60)
print("SEARCHING FOR FLAG PATTERNS")
print("=" * 60)

# Look for all occurrences of { and }
brace_positions = []
for i, char in enumerate(message_text):
    if char == '{' or char == '}':
        context_start = max(0, i-10)
        context_end = min(len(message_text), i+10)
        context = message_text[context_start:context_end]
        print(f"Position {i}: '{char}' - Context: {repr(context)}")
        brace_positions.append((i, char))

# Look for patterns like X{Y where X is 2-4 letters
print("\n" + "=" * 60)
print("LOOKING FOR FLAG-LIKE PATTERNS")
print("=" * 60)

# Search for patterns: word{...}
pattern = re.compile(r'[A-Za-z]{2,6}\{[^}]{0,50}\}', re.IGNORECASE)
matches = pattern.findall(message_text)
if matches:
    print(f"Found {len(matches)} potential flags:")
    for match in matches:
        print(f"  {match}")

# Also look for Kaal specifically
if 'Kaal' in message_text or 'kaal' in message_text.lower():
    print("\n🎯 Found 'Kaal' in message!")
    for match in re.finditer(r'[Kk]aal.{0,20}', message_text):
        print(f"  Position {match.start()}: {repr(match.group())}")

# Check if maybe the flag is in a different encoding or needs to be assembled
print("\n" + "=" * 60)
print("ANALYZING PATTERNS AROUND BRACES")
print("=" * 60)

# For each {, look at surrounding characters
for pos, char in brace_positions[:20]:  # First 20 occurrences
    if char == '{':
        # Get 20 chars before and after
        before = message_text[max(0, pos-20):pos]
        after = message_text[pos+1:min(len(message_text), pos+21)]
        
        # Check if it looks like a flag
        # Format should be: Kaal{xx_xx_xx}
        full_context = message_text[max(0, pos-10):min(len(message_text), pos+30)]
        
        print(f"\nPosition {pos}:")
        print(f"  Before: {repr(before[-10:])}")
        print(f"  After: {repr(after[:15])}")
        print(f"  Full: {repr(full_context)}")
        
        # Check if this could be the flag
        if '_' in after[:15]:
            print(f"  ⚠️  Contains underscore - might be flag!")

# Try to find the actual flag by looking for the pattern
print("\n" + "=" * 60)
print("DIRECT SEARCH FOR FLAG FORMAT")
print("=" * 60)

# The flag format is Kaal{xx_xx_xx}
# Let's search for any {xx_xx_xx} pattern
underscore_pattern = re.compile(r'\{[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}_[a-zA-Z0-9]{2}\}')
matches = underscore_pattern.findall(message_text)
if matches:
    print(f"Found {len(matches)} matches for {{xx_xx_xx}} pattern:")
    for match in matches:
        # Get context
        idx = message_text.find(match)
        context = message_text[max(0, idx-10):min(len(message_text), idx+len(match)+5)]
        print(f"  {repr(context)}")
        
        # Check what's before it
        before_10 = message_text[max(0, idx-10):idx]
        if any(word in before_10.lower() for word in ['kaal', 'laal', 'jaal', 'maal']):
            print(f"    🎯 POTENTIAL FLAG: {before_10[-4:]}{match}")

# Also try searching in the raw bytes
print("\n" + "=" * 60)
print("SEARCHING RAW BYTES")
print("=" * 60)

# Look for Kaal{ in bytes
if b'Kaal{' in message_bytes:
    idx = message_bytes.find(b'Kaal{')
    print(f"Found 'Kaal{{' at byte position {idx}")
    flag_bytes = message_bytes[idx:idx+50]
    print(f"Flag bytes: {flag_bytes}")
    print(f"Flag text: {flag_bytes.decode('latin-1', errors='ignore')}")
