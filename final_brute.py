#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re

def extract_flag(pdf_path, password):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                if reader.decrypt(password):
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    
                    flags = re.findall(r'BPCTF\{[^}]+\}', text)
                    if flags:
                        return password, text, flags
                    return password, text, None
    except:
        pass
    return None, None, None

pdf_path = Path("Cases/Flag_protected.pdf")
passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

# Generate all attempts
attempts = []

# Basic
attempts.append("".join(passwords_list))
attempts.append("".join([p.lower() for p in passwords_list]))
attempts.append(" ".join(passwords_list))
attempts.append(" ".join([p.lower() for p in passwords_list]))

# Leetspeak
def leet(text):
    return text.replace('A','4').replace('a','4').replace('E','3').replace('e','3').replace('I','1').replace('i','1').replace('O','0').replace('o','0').replace('S','5').replace('s','5').replace('T','7').replace('t','7')

for base in ["".join(passwords_list), " ".join(passwords_list), "".join([p.lower() for p in passwords_list])]:
    attempts.append(leet(base))

# Initials
attempts.append("".join([p[0] for p in passwords_list]))
attempts.append("".join([p[0].lower() for p in passwords_list]))

# With separators
for sep in ["_", "-", "."]:
    attempts.append(sep.join(passwords_list))
    attempts.append(sep.join([p.lower() for p in passwords_list]))

print(f"Trying {len(attempts)} passwords...")

for pwd in attempts:
    password, text, flags = extract_flag(pdf_path, pwd)
    if password:
        print(f"\nSUCCESS! Password: {password}")
        if flags:
            print("\nFLAG FOUND:")
            for flag in flags:
                print(flag)
        else:
            print("\nNo flag pattern found in text:")
            print(text[:500])
        break
else:
    print("\nNo password worked. Need different approach.")
