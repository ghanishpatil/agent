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

# Try with exact spacing from the hint
attempts = [
    "6 case password  fragments are pass",  # Double space
    "6 case password  fragments are pass  ",  # With trailing spaces
    "6casepassword fragments arepass",
    "6casepasswordfragmentsarepass",
    
    # Maybe it's telling us about the format?
    "VOICE CANNOT  SILENCE BUT  SYSTEM CAN",  # Double spaces
    "VOICECANNOTSILENCEBUTSYSTEMCAN",
    
    # Or maybe the number 6 is important?
    "6",
    "six",
    "Six",
    "SIX",
    
    # Or maybe it's about 6 fragments?
    "6fragments",
    "6Fragments",
    "6FRAGMENTS",
    
    # Try the exact hint text
    "6 case password fragments are pass",
    "6casepasswordfragmentsarepass",
    "6CasePasswordFragmentsArePass",
    
    # Maybe "pass" means password?
    "password",
    "PASSWORD",
    "Password",
    
    # Or maybe it's simpler - just the 6 words?
    "VOICE",
    "CANNOT",
    "SILENCE",
    "BUT",
    "SYSTEM",
    "CAN",
]

print(f"Trying {len(attempts)} passwords with exact spacing...")

for pwd in attempts:
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n*** FOUND: '{pwd}' ***\n")
        
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
    print(f"No: {repr(pwd)}")

print("\nStill no match.")
