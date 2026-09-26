#!/usr/bin/env python3
"""Recursively remove fillers until no more patterns"""

def remove_filler_once(text):
    """Remove one instance of filler pattern"""
    result = []
    i = 0
    removed = False
    while i < len(text):
        if not removed and i + 2 < len(text) and text[i] == text[i + 2]:
            result.append(text[i])
            i += 3
            removed = True
        else:
            result.append(text[i])
            i += 1
    return ''.join(result), removed

def remove_all_fillers(text):
    """Recursively remove all filler patterns"""
    while True:
        new_text, removed = remove_filler_once(text)
        if not removed:
            break
        print(f"  {text} -> {new_text}")
        text = new_text
    return text

candidates = [
    ("SPARTANS", "FUDRWMKXXTDIDDCPMR"),
    ("FRIENDS", "HKFAHPMWXCXKIIASPO"),
    ("OLDFRIENDSREUNION", "MONOMXUTVHSKIIAHPM"),
]

print("="*80)
print("RECURSIVE FILLER REMOVAL")
print("="*80)

for key, decrypted in candidates:
    print(f"\nKey: {key}")
    print(f"Decrypted: {decrypted}")
    final = remove_all_fillers(decrypted)
    print(f"Final: {final}")
    print(f"Flag: Kaal{{{final.lower()}}}")

print("\n" + "="*80)
