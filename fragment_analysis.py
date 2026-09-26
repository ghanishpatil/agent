#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re

def try_decrypt(pdf_path, password):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                result = reader.decrypt(password)
                if result:
                    return reader
    except:
        pass
    return None

pdf_path = Path("Cases/Flag_protected.pdf")
passwords = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

print("Analyzing 'fragments' hint...")
print("="*80)
print("Hint: '6 case password fragments are pass'")
print()
print("What if 'fragments' means:")
print("1. First letter of each password")
print("2. Last letter of each password")
print("3. First N letters")
print("4. Specific positions")
print()

wordlist = []

# First letters
first_letters = "".join([p[0] for p in passwords])
print(f"First letters: {first_letters}")
wordlist.append(first_letters)
wordlist.append(first_letters.lower())

# Last letters
last_letters = "".join([p[-1] for p in passwords])
print(f"Last letters: {last_letters}")
wordlist.append(last_letters)
wordlist.append(last_letters.lower())

# First 2 letters
first_two = "".join([p[:2] for p in passwords])
print(f"First 2 letters: {first_two}")
wordlist.append(first_two)
wordlist.append(first_two.lower())

# First 3 letters
first_three = "".join([p[:3] for p in passwords])
print(f"First 3 letters: {first_three}")
wordlist.append(first_three)
wordlist.append(first_three.lower())

# Middle letters
middle_letters = "".join([p[len(p)//2] for p in passwords])
print(f"Middle letters: {middle_letters}")
wordlist.append(middle_letters)
wordlist.append(middle_letters.lower())

# Alternating letters (1st, 3rd, 5th...)
alt_letters = ""
for p in passwords:
    for i in range(0, len(p), 2):
        alt_letters += p[i]
print(f"Alternating letters: {alt_letters}")
wordlist.append(alt_letters)
wordlist.append(alt_letters.lower())

# Level 3 leetspeak
def level3_leet(text):
    mapping = {
        'A': '4', 'a': '4', 'B': '8', 'b': '8', 'C': '(', 'c': '(',
        'E': '3', 'e': '3', 'G': '9', 'g': '9', 'I': '1', 'i': '1',
        'L': '1', 'l': '1', 'O': '0', 'o': '0', 'S': '5', 's': '5',
        'T': '7', 't': '7', 'Z': '2', 'z': '2',
    }
    return "".join([mapping.get(c, c) for c in text])

# Apply leetspeak to all
original_count = len(wordlist)
for i in range(original_count):
    wordlist.append(level3_leet(wordlist[i]))

# Also try with "pass" suffix
for i in range(len(wordlist)):
    wordlist.append(wordlist[i] + "pass")
    wordlist.append(wordlist[i] + "PASS")

print()
print(f"Testing {len(wordlist)} fragment-based passwords...")
print("="*80)

for pwd in wordlist:
    print(f"Trying: {pwd}")
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n{'='*80}")
        print(f"*** PASSWORD FOUND: {pwd} ***")
        print(f"{'='*80}\n")
        
        full_text = ""
        for page_num, page in enumerate(reader.pages, 1):
            try:
                text = page.extract_text()
                full_text += text
                print(f"PAGE {page_num}:")
                print("-"*80)
                print(text)
                print()
            except Exception as e:
                print(f"Error on page {page_num}: {e}")
        
        flags = re.findall(r'BPCTF\{[^}]+\}', full_text)
        if flags:
            print("\n" + "="*80)
            print("*** THE FLAG ***")
            print("="*80)
            for flag in flags:
                print(flag)
            print("="*80)
        
        exit(0)

print("\nFragment approach didn't work either.")
print("\nLet me try thinking about the PATTERN of how passwords were hidden...")
print()

# Pattern analysis
print("Password discovery methods:")
print("Case 2: Acrostic (first letters)")
print("Case 3: Direct text")
print("Case 4: Acrostic (first letters)")
print("Case 5: ASCII codes")
print("Case 6: Base64")
print("Case 7: Hex URL")
print()
print("What if the final password follows the SAME pattern?")
print()

# Try encoding the combined password in different ways
combined = "".join(passwords)

# ASCII codes (like Case 5)
ascii_pwd = " ".join([str(ord(c)) for c in combined])
print(f"ASCII: {ascii_pwd[:50]}...")
if try_decrypt(pdf_path, ascii_pwd):
    print("FOUND WITH ASCII!")
    exit(0)

# Base64 (like Case 6)
import base64
b64_pwd = base64.b64encode(combined.encode()).decode()
print(f"Base64: {b64_pwd}")
if try_decrypt(pdf_path, b64_pwd):
    print("FOUND WITH BASE64!")
    exit(0)

# Hex (like Case 7)
hex_pwd = combined.encode().hex()
print(f"Hex: {hex_pwd}")
if try_decrypt(pdf_path, hex_pwd):
    print("FOUND WITH HEX!")
    exit(0)

print("\nStill no match with encoding patterns.")
