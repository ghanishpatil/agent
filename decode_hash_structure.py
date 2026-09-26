#!/usr/bin/env python3
"""
Analyze PDF hash structure - Understanding what's inside
"""

import binascii

hash_str = "Flag_protected.pdf:$pdf$2*3*128*-4*1*16*673e550ef0e0dc44bcc60626d49cbe5f*32*546eb2a7fe18d9673752681aec6524c528bf4e5e4e758a4164004e56fffa0108*32*dda83f72209d9c40a42fc76eff707ae60b3691913c9a24b2f078b9c83b2ac2b9"

print("="*80)
print("PDF HASH STRUCTURE ANALYSIS")
print("="*80)

# Split the hash
parts = hash_str.split(':')[1].split('*')

print("\n[HASH COMPONENTS]")
print(f"1. Format: {parts[0]}")
print(f"2. Version: {parts[1]}")
print(f"3. Key Length: {parts[2]} bits")
print(f"4. Permission: {parts[3]}")
print(f"5. Encrypted Metadata: {parts[4]}")
print(f"6. ID Length: {parts[5]} bytes")
print(f"7. File ID: {parts[6]}")
print(f"8. U String Length: {parts[7]} bytes")
print(f"9. U String (User Password Hash): {parts[8]}")
print(f"10. O String Length: {parts[9]} bytes")
print(f"11. O String (Owner Password Hash): {parts[10]}")

print("\n" + "="*80)
print("WHAT EACH PART MEANS:")
print("="*80)

print("""
1. FORMAT ($pdf$2): PDF encryption version 2
2. VERSION (3): PDF specification revision 3
3. KEY LENGTH (128): AES-128 bit encryption
4. PERMISSION (-4): Access permissions flags
5. ENCRYPTED METADATA (1): Metadata is encrypted
6. FILE ID: Unique identifier for this PDF
7. U STRING: Encrypted user password verification
8. O STRING: Encrypted owner password verification

The U and O strings are the RESULT of:
  - Your password
  - + Random salt
  - + Multiple rounds of encryption (AES-128)
  - = One-way hash (cannot be reversed)
""")

print("="*80)
print("WHY YOU CAN'T DECODE IT:")
print("="*80)

print("""
1. ONE-WAY FUNCTION:
   Password → [AES Encryption] → Hash
   Hash → [???] → Password  ❌ IMPOSSIBLE

2. AES-128 ENCRYPTION:
   - Military-grade encryption
   - 2^128 possible keys (340,282,366,920,938,463,463,374,607,431,768,211,456)
   - Would take billions of years to try all combinations

3. NO MATHEMATICAL SHORTCUT:
   - No known algorithm to reverse AES
   - No pattern in the hash reveals the password
   - This is by design - it's SECURE

4. WHAT THE HASH CONTAINS:
   - Encrypted verification data
   - Random salt (different for each PDF)
   - NOT the password itself
   - NOT a simple encoding
""")

print("="*80)
print("ATTEMPTING TO EXTRACT ANY READABLE DATA:")
print("="*80)

# Try to decode hex strings
file_id = parts[6]
u_string = parts[8]
o_string = parts[10]

print(f"\nFile ID (hex): {file_id}")
try:
    file_id_bytes = binascii.unhexlify(file_id)
    print(f"File ID (bytes): {file_id_bytes}")
    print(f"File ID (ascii attempt): {file_id_bytes.decode('ascii', errors='ignore')}")
except:
    print("File ID: No readable ASCII data")

print(f"\nU String (hex): {u_string}")
try:
    u_bytes = binascii.unhexlify(u_string)
    print(f"U String (bytes): {u_bytes}")
    print(f"U String (ascii attempt): {u_bytes.decode('ascii', errors='ignore')}")
except:
    print("U String: No readable ASCII data")

print(f"\nO String (hex): {o_string}")
try:
    o_bytes = binascii.unhexlify(o_string)
    print(f"O String (bytes): {o_bytes}")
    print(f"O String (ascii attempt): {o_bytes.decode('ascii', errors='ignore')}")
except:
    print("O String: No readable ASCII data")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)

print("""
❌ The hash CANNOT be decoded/reversed
❌ The password is NOT hidden in the hash
❌ There is NO mathematical trick to extract it

✅ The ONLY way to get the password is:
   1. Try passwords until one works (brute force)
   2. Use a wordlist of likely passwords
   3. Find a hint in the challenge files
   4. Use GPU acceleration (hashcat) for speed

The hash is like a locked safe:
- You can see the safe (hash)
- You can't see what's inside (password)
- You must try combinations (crack it)
- Or find the key (hint in challenge)
""")

print("\n" + "="*80)
print("WHAT YOU SHOULD DO:")
print("="*80)

print("""
1. Look for MORE HINTS in the case files
   - Check metadata of all PDFs
   - Look for hidden text
   - Check for patterns in the cases

2. Use hashcat/john with wordlists
   - Much faster than Python
   - Can try millions of passwords per second

3. Think about the CHALLENGE THEME:
   - "Bleeding Press Index"
   - "LeetSpeak Unlocks"
   - 6 password fragments
   - What pattern makes sense?

The password exists, but it's not IN the hash.
The hash is just proof that you need the right password.
""")

print("="*80)
