#!/usr/bin/env python3
"""
Try ROT13 and other simple ciphers on the entire file
"""

with open(r'D:\mission-git-hackss\flight_record.dat', 'rb') as f:
    data = f.read()

# Try ROT13 on all ASCII text
def rot13(text):
    result = []
    for char in text:
        if 'a' <= char <= 'z':
            result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
        elif 'A' <= char <= 'Z':
            result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
        else:
            result.append(char)
    return ''.join(result)

# Extract ASCII text
text = ''.join(chr(b) if 32 <= b <= 126 else ' ' for b in data)

# Try ROT13
rotated = rot13(text)
if 'Kaal{' in rotated or 'kaal{' in rotated:
    idx = rotated.lower().index('kaal{')
    print("FLAG FOUND with ROT13:")
    print(rotated[idx:idx+100])
else:
    # Try all ROT variations
    for shift in range(1, 26):
        shifted = ''
        for char in text:
            if 'a' <= char <= 'z':
                shifted += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                shifted += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            else:
                shifted += char
        
        if 'Kaal{' in shifted or 'kaal{' in shifted:
            idx = shifted.lower().index('kaal{')
            print(f"FLAG FOUND with ROT{shift}:")
            print(shifted[idx:idx+100])
            break
    else:
        print("No flag found with ROT ciphers")

# Also try reverse
reversed_text = text[::-1]
if 'Kaal{' in reversed_text or '}laaK' in reversed_text:
    print("\nFLAG FOUND in reversed text!")
    if 'Kaal{' in reversed_text:
        idx = reversed_text.index('Kaal{')
        print(reversed_text[idx:idx+100])
    else:
        idx = reversed_text.index('}laaK')
        print(reversed_text[idx-100:idx+10])
