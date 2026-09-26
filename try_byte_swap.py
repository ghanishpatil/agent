import wave
import struct

audio_path = r"D:\mission-git-hackss\chall.wav"

print("=" * 60)
print("TRYING BYTE SWAP FIX")
print("=" * 60)

# Read the entire file
with open(audio_path, 'rb') as f:
    all_data = bytearray(f.read())

print(f"File size: {len(all_data)} bytes")

# Find the data chunk
data_pos = all_data.find(b'data')
if data_pos != -1:
    print(f"Found 'data' chunk at position: {data_pos}")
    # The data chunk header is: 'data' + 4 bytes size
    data_size = struct.unpack('<I', all_data[data_pos+4:data_pos+8])[0]
    print(f"Data chunk size: {data_size} bytes")
    
    audio_start = data_pos + 8
    audio_end = audio_start + data_size
    
    print(f"Audio data: bytes {audio_start} to {audio_end}")
    
    # Show first few bytes
    print(f"\nFirst 40 bytes of audio data (hex):")
    for i in range(20):
        pos = audio_start + i * 2
        byte1 = all_data[pos]
        byte2 = all_data[pos + 1]
        print(f"  Sample {i}: {byte2:02x} {byte1:02x} (little-endian: {byte1:02x}{byte2:02x})")
    
    # The pattern shows: byte1 is always 00, byte2 has the data
    # This means the bytes are in the wrong order!
    # In little-endian 16-bit audio, the LSB should come first, then MSB
    # But here we have: 00 FF, 00 02, 00 10, etc.
    # This should be: FF 00, 02 00, 10 00, etc. (which is what we see)
    
    # Wait, that's actually correct for little-endian!
    # Let me check if the issue is that the data should be in the LOWER byte
    
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print("Current format: [LSB=00] [MSB=data]")
    print("This means all actual audio is in the upper byte")
    print("The 'mistake' is that the lower byte is empty!")
    print("\nTo fix: Move upper byte to lower byte (shift right 8)")
    print("OR: Swap the bytes so [LSB=data] [MSB=00]")
    
    # Method 1: Swap bytes (so data moves to LSB position)
    fixed_data_swap = bytearray(all_data)
    for i in range(audio_start, audio_end, 2):
        fixed_data_swap[i], fixed_data_swap[i+1] = fixed_data_swap[i+1], fixed_data_swap[i]
    
    with open('chall_swapped.wav', 'wb') as f:
        f.write(fixed_data_swap)
    print("\n✓ Byte-swapped version saved to: chall_swapped.wav")
    
    # Now check if there's a message in the swapped version
    with wave.open('chall_swapped.wav', 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        import numpy as np
        samples = np.frombuffer(frames, dtype=np.int16)
        
        print(f"\nSwapped samples (first 20): {samples[:20]}")
        
        # Check LSB
        lsb_bits = samples & 1
        lsb_bytes = []
        for i in range(0, len(lsb_bits) - 7, 8):
            byte_val = 0
            for j in range(8):
                byte_val |= (lsb_bits[i + j] << j)
            lsb_bytes.append(byte_val)
        
        lsb_data = bytes(lsb_bytes)
        lsb_str = lsb_data.decode('latin-1', errors='ignore')
        
        print(f"\nLSB from swapped (first 300 chars):")
        print(repr(lsb_str[:300]))
        
        if 'Kaal{' in lsb_str or 'kaal{' in lsb_str.lower():
            print(f"\n🎯 FLAG FOUND IN SWAPPED VERSION!")
            start = lsb_str.lower().find('kaal{')
            if start != -1:
                flag_section = lsb_str[start:start+100]
                end = flag_section.find('}')
                if end != -1:
                    flag = flag_section[:end+1]
                    print(f"✓ FLAG: {flag}")
        
        # Also check all bit positions
        for bit_pos in range(8):
            bit_values = (samples >> bit_pos) & 1
            extracted_bytes = []
            for i in range(0, len(bit_values) - 7, 8):
                byte_val = 0
                for j in range(8):
                    byte_val |= (bit_values[i + j] << j)
                extracted_bytes.append(byte_val)
            
            extracted_data = bytes(extracted_bytes)
            extracted_str = extracted_data.decode('latin-1', errors='ignore')
            
            if 'Kaal{' in extracted_str or 'kaal{' in extracted_str.lower():
                print(f"\n🎯 FLAG IN BIT {bit_pos} OF SWAPPED!")
                start = extracted_str.lower().find('kaal{')
                if start != -1:
                    print(extracted_str[start:start+100])
