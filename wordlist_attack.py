#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re

def try_decrypt(pdf_path, password):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                if reader.decrypt(password):
                    return reader
    except:
        pass
    return None

pdf_path = Path("Cases/Flag_protected.pdf")

# Read wordlist
with open("custom_wordlist.txt", "r") as f:
    wordlist = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(wordlist)} passwords from wordlist")
print("Starting attack...")
print("="*80)

for i, pwd in enumerate(wordlist):
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n*** PASSWORD FOUND: {pwd} ***\n")
        
        for page in reader.pages:
            text = page.extract_text()
            print(text)
            
            flags = re.findall(r'BPCTF\{[^}]+\}', text)
            if flags:
                print("\n" + "="*80)
                print("FLAG:")
                for flag in flags:
                    print(flag)
        exit(0)
    
    if (i + 1) % 10 == 0:
        print(f"Tried {i + 1}/{len(wordlist)}...")

print(f"\nWordlist exhausted. Trying extended variations...")

# Generate more variations on the fly
passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

# Try EVERY permutation (this will take time)
import itertools

print("\nTrying permutations of 2 words...")
for r in [2, 3]:
    for perm in itertools.permutations(passwords_list, r):
        pwd = "".join(perm)
        reader = try_decrypt(pdf_path, pwd)
        if reader:
            print(f"\n*** FOUND: {pwd} ***")
            for page in reader.pages:
                text = page.extract_text()
                print(text)
                flags = re.findall(r'BPCTF\{[^}]+\}', text)
                if flags:
                    for flag in flags:
                        print(f"\nFLAG: {flag}")
            exit(0)

print("\nNo password found in permutations either.")
