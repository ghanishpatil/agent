import wave
import struct

wav_path = r"D:\mission-git-hackss\chall (1).wav"

print("=== Trying Common Steganography Patterns ===\n")

# Read file
with open(wav_path, 'rb') as f:
    data = f.read()

# Read as WAV
with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())

samples = struct.unpack(f'<{len(frames)//2}h', frames)

# Method 1: Check if LSB of consecutive bytes forms the message
print("1. Extracting LSB from consecutive sample bytes...")
lsb_sequence = []
for i in range(0, len(frames), 1):
    lsb_sequence.append(frames[i] & 1)

# Convert to bytes (8 bits at a time)
message_bytes = []
for i in range(0, len(lsb_sequence) - 8, 8):
    byte_val = 0
    for j in range(8):
        byte_val |= (lsb_sequence[i+j] << j)
    message_bytes.append(byte_val)

message = bytes(message_bytes)

if b'Kaal{' in message:
    pos = message.find(b'Kaal{')
    end = message.find(b'}', pos)
    if end != -1:
        flag = message[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG FOUND: {flag}")
else:
    print(f"First 200 bytes: {message[:200]}")

# Method 2: Check 2-LSB encoding
print("\n2. Trying 2-bit LSB encoding...")
bits_2lsb = []
for sample in samples:
    bits_2lsb.append(sample & 0x03)  # Get 2 LSBs

# Convert pairs to bytes
bytes_2lsb = []
for i in range(0, len(bits_2lsb) - 4, 4):
    byte_val = 0
    for j in range(4):
        byte_val |= (bits_2lsb[i+j] << (j*2))
    bytes_2lsb.append(byte_val)

message_2lsb = bytes(bytes_2lsb)

if b'Kaal{' in message_2lsb:
    pos = message_2lsb.find(b'Kaal{')
    end = message_2lsb.find(b'}', pos)
    if end != -1:
        flag = message_2lsb[pos:end+1].decode('ascii', errors='ignore')
        print(f"\n✓ FLAG FOUND: {flag}")

# Method 3: Check if the "mistake" is a single flipped bit in the flag
print("\n3. Searching for near-flag patterns...")
# Look through all the data for patterns close to "Kaal{"
target = b'Kaal{'
for i in range(len(data) - len(target)):
    chunk = data[i:i+len(target)]
    # Count how many bits are different
    diff_count = 0
    for j in range(len(target)):
        xor = chunk[j] ^ target[j]
        diff_count += bin(xor).count('1')
    
    # If only 1 bit is different, we found it!
    if diff_count == 1:
        print(f"\n✓ Found near-match at position {i}!")
        print(f"Found: {chunk}")
        print(f"Expected: {target}")
        
        # Find which bit and fix it
        for j in range(len(target)):
            if chunk[j] != target[j]:
                print(f"Byte {j}: {chunk[j]:02x} should be {target[j]:02x}")
                print(f"Bit difference: {chunk[j] ^ target[j]:02x}")
        
        # Extract the flag
        context = data[i:i+100]
        print(f"\nContext: {context}")
        
        # Try to extract flag by fixing the bit
        fixed_data = bytearray(data)
        for j in range(len(target)):
            if chunk[j] != target[j]:
                fixed_data[i+j] = target[j]
        
        end_pos = fixed_data.find(b'}', i)
        if end_pos != -1:
            flag = fixed_data[i:end_pos+1].decode('ascii', errors='ignore')
            print(f"\n✓✓✓ FLAG: {flag}")
            break

# Method 4: Check if samples encode ASCII directly with offset
print("\n4. Checking if samples are ASCII with offset...")
for offset in [0, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]:
    test_bytes = bytes([(abs(s) + offset) & 0xFF for s in samples[:10000]])
    if b'Kaal{' in test_bytes:
        print(f"\n✓ Found with offset {offset}!")
        pos = test_bytes.find(b'Kaal{')
        
        # Apply to full data
        full_bytes = bytes([(abs(s) + offset) & 0xFF for s in samples])
        end = full_bytes.find(b'}', pos)
        if end != -1:
            flag = full_bytes[pos:end+1].decode('ascii', errors='ignore')
            print(f"\nFLAG: {flag}")
            break

print("\n=== Analysis Complete ===")
