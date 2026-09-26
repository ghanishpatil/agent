#!/usr/bin/env python3

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

# Search for all potential encrypted data
print("[*] Searching entire binary for XOR-encrypted 'Kaal{'...")

target = b'Kaal{'
found_any = False

for offset in range(len(data) - 50):
    chunk = data[offset:offset+50]
    
    # Try all single-byte XOR keys
    for key in range(1, 256):
        try:
            decrypted = bytes([b ^ key for b in chunk[:5]])
            if decrypted == target:
                # Found potential match
                full_decrypt = bytes([b ^ key for b in chunk])
                
                # Check if it looks like a valid flag
                flag_end = full_decrypt.find(b'}')
                if flag_end > 0 and flag_end < 40:
                    flag = full_decrypt[:flag_end+1].decode('ascii', errors='ignore')
                    if flag.startswith('Kaal{') and flag.count('{') == 1 and flag.count('}') == 1:
                        print(f"\n[+] FOUND at offset {hex(offset)}")
                        print(f"    XOR key: {key} (0x{key:02x}, '{chr(key) if 32 <= key < 127 else '?'}')")
                        print(f"    FLAG: {flag}")
                        found_any = True
        except:
            pass

if not found_any:
    print("[-] No XOR-encrypted flag found")
    
    # Try looking for the key itself
    print("\n[*] Looking for hardcoded key in binary...")
    for s in [b'key', b'KEY', b'Kaal', b'secret', b'password']:
        if s in data:
            idx = data.find(s)
            print(f"  Found '{s.decode()}' at {hex(idx)}")
