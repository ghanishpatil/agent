#!/usr/bin/env python3
"""
Try simple flag variations based on the challenge
"""

# The fake flag decodes to: "i_think_this_is_wrong"
# So what would be RIGHT?

possible_flags = [
    "Kaal{i_think_this_is_right}",
    "Kaal{i_know_this_is_right}",
    "Kaal{this_is_right}",
    "Kaal{this_is_correct}",
    "Kaal{laddoos_are_mine}",
    "Kaal{bheem_got_laddoos}",
    "Kaal{double_layer_mischief}",
    "Kaal{hidden_in_audio}",
    "Kaal{RIFX_not_RIFF}",
    "Kaal{wrong_key_right_flag}",
    "Kaal{i_think_this_is_correct}",
    "Kaal{1_kn0w_th15_15_r1ght}",
    "Kaal{gn0rw_51_51ht_kn1ht_1}",  # Reversed
]

print("[*] Possible flags to try:")
for flag in possible_flags:
    print(f"    {flag}")

# But let's also check if there's something in the RIFX vs RIFF difference
print("\n[*] Analyzing RIFX header...")
with open('chall_media/chall_media.mp3', 'rb') as f:
    header = f.read(100)

print(f"    Header (hex): {header[:50].hex()}")
print(f"    Header (ASCII): {header[:50]}")

# RIFX = 52 49 46 58
# RIFF = 52 49 46 46
# The difference is X vs F in the 4th byte
# X = 0x58, F = 0x46
# Difference = 0x58 - 0x46 = 0x12 = 18

print(f"\n[*] RIFX vs RIFF analysis:")
print(f"    RIFX 4th byte: 0x58 (X)")
print(f"    RIFF 4th byte: 0x46 (F)")
print(f"    Difference: 0x{0x58 - 0x46:02x} = {0x58 - 0x46}")

# Maybe the flag is encoded with this difference?

# Let's also check if the "double layer" means:
# Layer 1: The fake flag in plaintext
# Layer 2: The real flag hidden in steganography

# Since we can't use steghide, let me try one more LSB method
print("\n[*] Final LSB attempt with correct bit order...")

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

data_pos = data.find(b'data')
if data_pos != -1:
    import struct
    data_size = struct.unpack('<I', data[data_pos+4:data_pos+8])[0]
    audio_data = data[data_pos+8:data_pos+8+data_size]
    
    # Extract LSB from each byte, MSB first (standard LSB steganography)
    bits = []
    for byte in audio_data[:200000]:  # First 200KB
        bits.append(byte & 1)
    
    # Convert to bytes (MSB first)
    extracted_bytes = []
    for i in range(0, len(bits), 8):
        if i + 7 < len(bits):
            byte_val = 0
            for j in range(8):
                byte_val = (byte_val << 1) | bits[i + j]
            extracted_bytes.append(byte_val)
    
    extracted_data = bytes(extracted_bytes)
    
    # Save it
    with open('lsb_final.bin', 'wb') as f:
        f.write(extracted_data)
    
    print(f"    Saved LSB data to lsb_final.bin ({len(extracted_data)} bytes)")
    
    # Look for flag
    import re
    flag_match = re.search(rb'Kaal\{[^}]+\}', extracted_data)
    if flag_match:
        print(f"\n[+] *** REAL FLAG IN LSB ***: {flag_match.group().decode('utf-8', errors='ignore')}")
    
    # Look for any readable text
    text_matches = re.findall(rb'[\x20-\x7e]{30,}', extracted_data)
    if text_matches:
        print(f"\n[*] Long readable strings in LSB:")
        for text in text_matches[:20]:
            decoded = text.decode('utf-8', errors='ignore')
            print(f"    {decoded}")
    
    # Check first 1000 bytes
    print(f"\n[*] First 500 bytes of LSB data:")
    print(extracted_data[:500])

print("\n[*] Complete!")
