#!/usr/bin/env python3
import struct

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

# Find "Enter key:" and look at nearby data
enter_key_idx = data.find(b'Enter key:')
if enter_key_idx != -1:
    print(f"[*] Found 'Enter key:' at offset {hex(enter_key_idx)}")
    print(f"    Context: {data[enter_key_idx-50:enter_key_idx+100]}")

# Find "Flag:" and look at nearby data
flag_idx = data.find(b'Flag:')
if flag_idx != -1:
    print(f"\n[*] Found 'Flag:' at offset {hex(flag_idx)}")
    print(f"    Context: {data[flag_idx-50:flag_idx+100]}")

# Find "Wrong" and look at nearby data
wrong_idx = data.find(b'Wrong')
if wrong_idx != -1:
    print(f"\n[*] Found 'Wrong' at offset {hex(wrong_idx)}")
    print(f"    Context: {data[wrong_idx-50:wrong_idx+100]}")

# Look for encrypted flag pattern
print("\n[*] Searching for encrypted data patterns...")
for i in range(len(data) - 40):
    chunk = data[i:i+40]
    # Check if it looks like encrypted data (high entropy, no nulls)
    if b'\x00' not in chunk and len(set(chunk)) > 20:
        # Check if nearby there's a reference to it
        if i > 1000 and i < len(data) - 1000:
            if b'Flag' in data[max(0,i-200):i+200] or b'key' in data[max(0,i-200):i+200]:
                print(f"  Possible encrypted data at {hex(i)}: {chunk.hex()[:60]}")
                break
