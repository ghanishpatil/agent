#!/usr/bin/env python3
import pikepdf
import re

passwords = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]
combined = "VOICECANNOTSILENCEBUTSYSTEMCAN"

def caesar_cipher(text, shift):
    result = ""
    for char in text:
        if 'a' <= char <= 'z':
            result += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
        elif 'A' <= char <= 'Z':
            result += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
        else:
            result += char
    return result

wordlist = []

# Try all Caesar cipher shifts (0-25)
for shift in range(26):
    wordlist.append(caesar_cipher(combined, shift))
    wordlist.append(caesar_cipher(combined.lower(), shift))

# Try Atbash cipher (reverse alphabet)
def atbash(text):
    result = ""
    for char in text:
        if 'a' <= char <= 'z':
            result += chr(ord('z') - (ord(char) - ord('a')))
        elif 'A' <= char <= 'Z':
            result += chr(ord('Z') - (ord(char) - ord('A')))
        else:
            result += char
    return result

wordlist.append(atbash(combined))
wordlist.append(atbash(combined.lower()))

# Try reversing
wordlist.append(combined[::-1])
wordlist.append(combined.lower()[::-1])

# Try XOR with common keys
def xor_string(text, key):
    return "".join(chr(ord(c) ^ key) for c in text)

for key in range(1, 256):
    try:
        xored = xor_string(combined, key)
        if xored.isprintable():
            wordlist.append(xored)
    except:
        pass

print(f"Testing {len(wordlist)} cipher variations...")
print("="*80)

for pwd in wordlist:
    try:
        with pikepdf.open("Cases/Flag_protected.pdf", password=pwd) as pdf:
            print(f"\n{'='*80}")
            print(f"*** PASSWORD FOUND: {pwd} ***")
            print(f"{'='*80}\n")
            
            text = ""
            for page in pdf.pages:
                t = page.extract_text()
                text += t
                print(t)
                print("-"*80)
            
            flags = re.findall(r'BPCTF\{[^}]+\}', text)
            if flags:
                print("\n" + "="*80)
                print("*** THE FLAG ***")
                print("="*80)
                print(flags[0])
                print("="*80)
            exit(0)
    except:
        pass

print("\nCipher variations didn't work.")
