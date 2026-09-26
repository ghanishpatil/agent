#!/usr/bin/env python3
"""
Verify that the collision files are actually different
"""

import hashlib

collision1_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89
55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70
"""

collision2_hex = """
d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89
55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70
"""

file1 = bytes.fromhex(collision1_hex.replace('\n', ''))
file2 = bytes.fromhex(collision2_hex.replace('\n', ''))

print(f"File 1 length: {len(file1)}")
print(f"File 2 length: {len(file2)}")
print(f"Files are different: {file1 != file2}")

print(f"\nFile 1 MD5: {hashlib.md5(file1).hexdigest()}")
print(f"File 2 MD5: {hashlib.md5(file2).hexdigest()}")
print(f"MD5 collision: {hashlib.md5(file1).hexdigest() == hashlib.md5(file2).hexdigest()}")

# Find the differences
print(f"\nFinding byte differences...")
diffs = []
for i in range(len(file1)):
    if file1[i] != file2[i]:
        diffs.append((i, file1[i], file2[i]))

print(f"Number of different bytes: {len(diffs)}")
print(f"Differences at positions:")
for pos, b1, b2 in diffs[:10]:  # Show first 10
    print(f"  Position {pos}: 0x{b1:02x} vs 0x{b2:02x}")

# Save to files
with open("coll1.bin", "wb") as f:
    f.write(file1)
with open("coll2.bin", "wb") as f:
    f.write(file2)

print(f"\n[+] Files saved as coll1.bin and coll2.bin")
