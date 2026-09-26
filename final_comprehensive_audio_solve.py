import wave
import struct

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Final Comprehensive Audio Solve ===\n")

# Read everything
with open(wav_path, 'rb') as f:
    raw_data = f.read()

with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    params = wav.getparams()

samples = struct.unpack(f'<{len(frames)//2}h', frames)

print(f"File size: {len(raw_data)} bytes")
print(f"Samples: {len(samples)}")
print(f"Parameters: {params}")

# The challenge says "one small mistake" - let's check if there's a typo in embedded text
# or if we need to correct a single character

# Extract all possible text from the file
print("\n=== Extracting All Readable Text ===")
readable_chunks = []
current_chunk = []

for byte in raw_data:
    if 32 <= byte <= 126:  # Printable ASCII
        current_chunk.append(chr(byte))
    else:
        if len(current_chunk) >= 5:  # Only keep chunks of 5+ characters
            readable_chunks.append(''.join(current_chunk))
        current_chunk = []

if current_chunk and len(current_chunk) >= 5:
    readable_chunks.append(''.join(current_chunk))

print(f"Found {len(readable_chunks)} readable text chunks")
for i, chunk in enumerate(readable_chunks[:20]):  # Show first 20
    print(f"{i}: {chunk}")
    
    # Check for flag-like patterns
    if 'aal' in chunk.lower() or 'flag' in chunk.lower():
        print(f"  *** Potential flag chunk! ***")

# Check if "Kaal" appears with wrong bracket
print("\n=== Checking for Typos in Flag Format ===")
typo_patterns = [
    'Kaal[', 'Kaal(', 'Kaal}', 'Kaal<', 'Kaal>',
    'Kaai{', 'Kaal{', 'Kaal{', 'Kaal{',
    'kaal{', 'KAAL{', 'KaaL{', 'KAal{',
]

for pattern in typo_patterns:
    if pattern.encode() in raw_data:
        pos = raw_data.find(pattern.encode())
        print(f"\n✓ Found '{pattern}' at position {pos}!")
        context = raw_data[pos:pos+100]
        print(f"Context: {context}")
        
        # Try to extract the full flag
        end_pos = context.find(b'}')
        if end_pos == -1:
            end_pos = context.find(b']')
        if end_pos == -1:
            end_pos = context.find(b')')
        
        if end_pos != -1:
            potential_flag = context[:end_pos+1].decode('ascii', errors='ignore')
            print(f"Potential flag: {potential_flag}")
            
            # Fix the typo if needed
            if pattern != 'Kaal{':
                fixed_flag = potential_flag.replace(pattern, 'Kaal{')
                if pattern.endswith('[') or pattern.endswith('(') or pattern.endswith('}'):
                    fixed_flag = fixed_flag[:-1] + '}'
                print(f"Fixed flag: {fixed_flag}")

# Try spectral analysis hint - maybe we need to use a tool
print("\n=== Hint for Manual Analysis ===")
print("If automated methods don't work, try:")
print("1. Open the WAV file in Audacity")
print("2. Go to Analyze > Plot Spectrum or View > Spectrogram")
print("3. Look for visual patterns or text in the spectrogram")
print("4. Try Effect > Reverse to play backwards")
print("5. Check for hidden messages in the waveform")

# One more try - check if the flag is in the metadata
print("\n=== Checking All Chunks for Hidden Data ===")
chunk_pos = 0
while chunk_pos < len(raw_data) - 8:
    chunk_id = raw_data[chunk_pos:chunk_pos+4]
    if chunk_id in [b'RIFF', b'fmt ', b'data', b'LIST', b'INFO']:
        chunk_pos += 1
        continue
    
    # Unknown chunk - might contain hidden data
    if all(32 <= b <= 126 for b in chunk_id):
        print(f"Found unknown chunk at {chunk_pos}: {chunk_id}")
        chunk_size_bytes = raw_data[chunk_pos+4:chunk_pos+8]
        if len(chunk_size_bytes) == 4:
            chunk_size = struct.unpack('<I', chunk_size_bytes)[0]
            if chunk_size < 10000:  # Reasonable size
                chunk_data = raw_data[chunk_pos+8:chunk_pos+8+chunk_size]
                print(f"Chunk data: {chunk_data[:100]}")
                
                if b'Kaal{' in chunk_data:
                    pos = chunk_data.find(b'Kaal{')
                    end = chunk_data.find(b'}', pos)
                    if end != -1:
                        flag = chunk_data[pos:end+1].decode('ascii', errors='ignore')
                        print(f"\n✓✓✓ FLAG FOUND: {flag}")
    
    chunk_pos += 1

print("\n=== Analysis Complete ===")
print("\nIf no flag was found automatically, the challenge likely requires:")
print("- Manual spectral analysis in Audacity")
print("- A specific steganography tool (DeepSound, Sonic Visualiser, etc.)")
print("- Or the 'one small mistake' is in how the audio should be interpreted")
