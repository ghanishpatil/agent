#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re

def try_password(pdf_path, password):
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

# The 6 passwords
passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

# Generate comprehensive list
attempts = []

# Basic combinations
attempts.append("VOICECANNOTSILENCEBUTSYSTEMCAN")
attempts.append("voicecannotsilencebutsystemcan")
attempts.append("VoiceCannotSilenceButSystemCan")

# With different separators
for sep in ["", " ", "_", "-", "."]:
    attempts.append(sep.join(passwords_list))
    attempts.append(sep.join([p.lower() for p in passwords_list]))
    attempts.append(sep.join([p.capitalize() for p in passwords_list]))

# Leetspeak variations - comprehensive
leet_mappings = [
    {'A':'4', 'E':'3', 'I':'1', 'O':'0', 'S':'5', 'T':'7'},
    {'A':'4', 'E':'3', 'I':'1', 'O':'0', 'S':'$', 'T':'7'},
    {'A':'@', 'E':'3', 'I':'!', 'O':'0', 'S':'5', 'T':'7'},
    {'A':'4', 'E':'3', 'I':'1', 'O':'0', 'S':'5', 'T':'7', 'B':'8', 'C':'('},
    {'a':'4', 'e':'3', 'i':'1', 'o':'0', 's':'5', 't':'7'},
]

base_strings = [
    "".join(passwords_list),
    " ".join(passwords_list),
    "".join([p.lower() for p in passwords_list]),
    " ".join([p.lower() for p in passwords_list]),
]

for base in base_strings:
    for lmap in leet_mappings:
        result = base
        for old, new in lmap.items():
            result = result.replace(old, new)
        attempts.append(result)

# First/last letter combinations
first = "".join([p[0] for p in passwords_list])
last = "".join([p[-1] for p in passwords_list])
attempts.extend([first, first.lower(), last, last.lower()])

# With "pass" prefix/suffix
for base in ["VOICECANNOTSILENCEBUTSYSTEMCAN", "voicecannotsilencebutsystemcan"]:
    attempts.append(f"pass{base}")
    attempts.append(f"{base}pass")
    attempts.append(f"PASS{base}")
    attempts.append(f"{base}PASS")

# Numbers
attempts.append("567363")  # lengths

# Reversed
attempts.append("NACMETSYSTUBECNELISTONNACECIOV")
attempts.append("CANVOICE")  # last + first

# Remove duplicates
attempts = list(dict.fromkeys(attempts))

print(f"Trying {len(attempts)} unique password combinations...")
print("="*60)

for i, pwd in enumerate(attempts):
    reader = try_password(pdf_path, pwd)
    if reader:
        print(f"\nSUCCESS! Password #{i+1}: {pwd}")
        print("\n" + "="*80)
        print("FLAG FILE CONTENT:")
        print("="*80)
        
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                print(f"\n--- PAGE {page_num + 1} ---")
                print(text)
                
                # Extract flag
                flags = re.findall(r'BPCTF\{[^}]+\}', text)
                if flags:
                    print("\n" + "="*80)
                    print("FLAG FOUND:")
                    print("="*80)
                    for flag in flags:
                        print(flag)
            except Exception as e:
                print(f"Error on page {page_num + 1}: {e}")
        break
    
    if (i + 1) % 50 == 0:
        print(f"Tried {i + 1} passwords...")
else:
    print("\nNo password worked from the generated list.")
    print("The password logic might be more complex.")
