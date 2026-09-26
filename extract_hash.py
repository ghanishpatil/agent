#!/usr/bin/env python3
import struct

# Extract PDF encryption info for hash cracking
with open("Cases/Flag_protected.pdf", "rb") as f:
    data = f.read()

# Look for encryption dictionary
if b'/Encrypt' in data:
    print("PDF is encrypted")
    
    # Find encryption parameters
    encrypt_start = data.find(b'/Encrypt')
    section = data[encrypt_start:encrypt_start+500]
    
    print("\nEncryption section:")
    print(section[:200].decode('latin-1', errors='ignore'))
    
    # Look for /O and /U strings (owner and user passwords)
    if b'/O' in section:
        print("\nFound /O (owner password hash)")
    if b'/U' in section:
        print("\nFound /U (user password hash)")
    
    # Look for /R (revision)
    if b'/R' in data:
        r_pos = data.find(b'/R')
        r_section = data[r_pos:r_pos+20]
        print(f"\nRevision info: {r_section}")
    
    # Look for /P (permissions)
    if b'/P' in data:
        p_pos = data.find(b'/P')
        p_section = data[r_pos:p_pos+20]
        print(f"\nPermissions: {p_section}")

print("\n" + "="*80)
print("To crack this with John the Ripper:")
print("1. Install John the Ripper")
print("2. Run: pdf2john.pl Flag_protected.pdf > hash.txt")
print("3. Run: john --wordlist=wordlist.txt hash.txt")
print("="*80)
