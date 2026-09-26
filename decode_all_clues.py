#!/usr/bin/env python3
"""
Try to decode flag from all available clues
"""
import hashlib
import base64

# All clues from EXIF
model = "Sun Microsystems Netra T1"
copyright_msg = "Access restricted. Decryption key: https://bit.ly/3uJ6G9s"
artist = "Aris Thorne"
datetime = "2001:09:26 11:42:04"
node_id = "EXDS-SN-1102-SC"
archive = "exodus-infrastructure-recovery"

# Company info
company = "Exodus Communications"
bankruptcy_date = "September 26, 2001"

print("="*60)
print("ANALYZING ALL CLUES")
print("="*60)

# Try various combinations and encodings
print("\n1. Node ID analysis:")
parts = node_id.split("-")
print(f"   Parts: {parts}")
print(f"   EXDS: Exodus")
print(f"   SN: Serial Number")
print(f"   1102: ?")
print(f"   SC: ?")

print("\n2. Date analysis:")
print(f"   Date: 2001-09-26")
print(f"   Time: 11:42:04")
print(f"   Unix timestamp: ?")

print("\n3. Archive name:")
print(f"   {archive}")

print("\n4. Artist name:")
print(f"   {artist}")
print(f"   Without space: ArisThorne")
print(f"   Lowercase: aristhorne")

# Try MD5/SHA hashes
print("\n5. Hash attempts:")
for text in [artist, node_id, archive, company]:
    md5 = hashlib.md5(text.encode()).hexdigest()
    print(f"   MD5({text}): {md5[:16]}...")

# Try base64
print("\n6. Base64 attempts:")
for text in [artist, node_id, archive]:
    b64 = base64.b64encode(text.encode()).decode()
    print(f"   B64({text}): {b64}")

# Check if there's a pattern in the numbers
print("\n7. Number analysis:")
print(f"   1102 in different bases:")
print(f"   - Decimal: 1102")
print(f"   - Hex: 0x{1102:x}")
print(f"   - Binary: {bin(1102)}")
print(f"   - ASCII: {chr(1102 % 256) if 1102 % 256 < 128 else 'N/A'}")

# Try combining elements
print("\n8. Possible flag combinations:")
flags = [
    f"Kaal{{{artist.replace(' ', '')}}}",
    f"Kaal{{{artist.replace(' ', '_')}}}",
    f"Kaal{{{node_id}}}",
    f"Kaal{{{archive}}}",
    f"Kaal{{{artist}_{node_id}}}",
    f"Kaal{{{company.replace(' ', '')}}}",
    f"Kaal{{aristhorne}}",
    f"Kaal{{ArisThorne}}",
]

for flag in flags:
    print(f"   {flag}")
