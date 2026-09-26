#!/usr/bin/env python3

candidates = [
    ("SPARTANS", "FUDRWMKXXTDIDDCPMR"),
    ("FRIENDS", "HKFAHPMWXXKIIASPO"),
    ("OLDFRIENDSREUNION", "MOOMXUTVHSKIIAHPM"),
]

def remove_filler(text):
    result = []
    i = 0
    while i < len(text):
        if i < len(text) - 2 and text[i] == text[i+2]:
            result.append(text[i])
            i += 2
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)

print("="*60)
for key, decrypted in candidates:
    cleaned = remove_filler(decrypted)
    print(f"Key: {key}")
    print(f"  Decrypted: {decrypted}")
    print(f"  Cleaned:   {cleaned}")
    print(f"  Flag: Kaal{{{cleaned.lower()}}}")
    print()
