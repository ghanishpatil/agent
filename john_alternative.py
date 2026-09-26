#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re
import itertools

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

# Level 3 Leetspeak mapping (aggressive)
def level3_leet(text):
    mapping = {
        'A': '4', 'a': '4',
        'B': '8', 'b': '8',
        'C': '(', 'c': '(',
        'E': '3', 'e': '3',
        'G': '9', 'g': '9',
        'I': '1', 'i': '1',
        'L': '1', 'l': '1',
        'O': '0', 'o': '0',
        'S': '5', 's': '5',
        'T': '7', 't': '7',
        'Z': '2', 'z': '2',
    }
    result = ""
    for char in text:
        result += mapping.get(char, char)
    return result

# Generate comprehensive wordlist
wordlist = []

# CRITICAL OBSERVATIONS:
# 1. "LeetSpeak Unlo cks" - space in "Unlo cks" 
# 2. "6 case password  fragments are pass" - double space before "fragments"
# 3. Metadata says "Level - 3"
# 4. The word "pass" appears at the end

# Base combinations
bases = []

# All passwords joined different ways
for sep in ['', ' ', '_', '-', '.']:
    bases.append(sep.join(passwords))
    bases.append(sep.join([p.lower() for p in passwords]))
    bases.append(sep.join([p.capitalize() for p in passwords]))

# With "pass" at the end (from hint)
for sep in ['', ' ', '_', '-']:
    bases.append(sep.join(passwords) + sep + "pass")
    bases.append(sep.join([p.lower() for p in passwords]) + sep + "pass")

# Apply leetspeak to all bases
for base in bases:
    wordlist.append(base)  # Original
    wordlist.append(level3_leet(base))  # Level 3 leetspeak

# Try partial leetspeak (only some words)
for i in range(len(passwords)):
    temp = passwords.copy()
    temp[i] = level3_leet(temp[i])
    wordlist.append("".join(temp))
    wordlist.append(" ".join(temp))
    wordlist.append("_".join(temp))

# Try the message itself
message = "VOICECANNOTSILENCEBUTSYSTEMCAN"
wordlist.extend([
    message,
    level3_leet(message),
    message.lower(),
    level3_leet(message.lower()),
    "Voice Cannot Silence But System Can",
    level3_leet("Voice Cannot Silence But System Can"),
])

# Try with "Unlo cks" pattern (space in middle)
for pwd in passwords:
    mid = len(pwd) // 2
    spaced = pwd[:mid] + " " + pwd[mid:]
    wordlist.append(spaced)
    wordlist.append(level3_leet(spaced))

# Try double space pattern
wordlist.append("  ".join(passwords))
wordlist.append(level3_leet("  ".join(passwords)))

# Try fragments (first 3, last 3, etc)
wordlist.append("".join(passwords[:3]))
wordlist.append("".join(passwords[3:]))
wordlist.append(level3_leet("".join(passwords[:3])))
wordlist.append(level3_leet("".join(passwords[3:])))

# Remove duplicates
wordlist = list(set(wordlist))

print(f"Testing {len(wordlist)} password combinations...")
print("="*80)

for i, pwd in enumerate(wordlist, 1):
    if i % 100 == 0:
        print(f"Tested {i}/{len(wordlist)}...")
    
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
        
        # Extract flag
        flags = re.findall(r'BPCTF\{[^}]+\}', full_text)
        if flags:
            print("\n" + "="*80)
            print("*** THE FLAG ***")
            print("="*80)
            for flag in flags:
                print(flag)
            print("="*80)
        else:
            print("\nNo flag found in standard format, full text above.")
        
        exit(0)

print(f"\nTested all {len(wordlist)} combinations. None worked.")
print("\nLet me try even more variations...")

# Nuclear option - try ALL permutations of the 6 passwords
print("\nTrying permutations (this may take a while)...")
count = 0
for perm in itertools.permutations(passwords):
    for sep in ['', ' ', '_']:
        pwd = sep.join(perm)
        count += 1
        if count % 500 == 0:
            print(f"Tested {count} permutations...")
        
        reader = try_decrypt(pdf_path, pwd)
        if reader:
            print(f"\n*** FOUND: {pwd} ***")
            exit(0)
        
        # Also try leetspeak version
        pwd_leet = level3_leet(pwd)
        reader = try_decrypt(pdf_path, pwd_leet)
        if reader:
            print(f"\n*** FOUND: {pwd_leet} ***")
            exit(0)

print(f"\nTested {count} permutations. Still no match.")
