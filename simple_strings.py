#!/usr/bin/env python3
"""
Simple strings extraction - just print ALL readable strings
"""

with open(r'D:\mission-git-hackss\flight_record.dat', 'rb') as f:
    data = f.read()

# Extract all strings of length 4 or more
current = []
all_strings = []

for byte in data:
    if 32 <= byte <= 126:  # Printable ASCII
        current.append(chr(byte))
    else:
        if len(current) >= 4:
            s = ''.join(current)
            all_strings.append(s)
            print(s)
        current = []

if len(current) >= 4:
    s = ''.join(current)
    all_strings.append(s)
    print(s)

# Search for Kaal in the combined strings
combined = ' '.join(all_strings)
if 'Kaal' in combined or 'kaal' in combined:
    print("\n\n=== FOUND KAAL ===")
    idx = combined.lower().index('kaal')
    print(combined[max(0, idx-50):idx+100])
