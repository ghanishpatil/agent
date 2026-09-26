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

# Level 3 Leetspeak - AGGRESSIVE
def level3_leet(text):
    """Apply Level 3 (aggressive) leetspeak"""
    result = text
    # Level 1 - Basic
    result = result.replace('A', '4').replace('a', '4')
    result = result.replace('E', '3').replace('e', '3')
    result = result.replace('I', '1').replace('i', '1')
    result = result.replace('O', '0').replace('o', '0')
    result = result.replace('S', '5').replace('s', '5')
    result = result.replace('T', '7').replace('t', '7')
    
    # Level 2 - Intermediate
    result = result.replace('B', '8').replace('b', '8')
    result = result.replace('G', '9').replace('g', '9')
    result = result.replace('L', '1').replace('l', '1')
    
    # Level 3 - Advanced
    result = result.replace('C', '(').replace('c', '(')
    result = result.replace('Z', '2').replace('z', '2')
    
    return result

passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

# Try Level 3 leetspeak on various combinations
attempts = []

# Base combinations
bases = [
    "".join(passwords_list),
    " ".join(passwords_list),
    "_".join(passwords_list),
    "-".join(passwords_list),
    "".join([p.lower() for p in passwords_list]),
    " ".join([p.lower() for p in passwords_list]),
]

for base in bases:
    attempts.append(level3_leet(base))

# Also try mixed case
attempts.append(level3_leet("VoiceCannotSilenceButSystemCan"))
attempts.append(level3_leet("voiceCannotSilenceButSystemCan"))

print("Trying Level 3 Leetspeak passwords...")
print("="*80)

for pwd in attempts:
    print(f"Trying: {pwd}")
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n*** PASSWORD FOUND: {pwd} ***\n")
        
        full_text = ""
        for page in reader.pages:
            try:
                text = page.extract_text()
                full_text += text
                print(text)
                print("\n" + "-"*80 + "\n")
            except Exception as e:
                print(f"Error: {e}")
        
        flags = re.findall(r'BPCTF\{[^}]+\}', full_text)
        if flags:
            print("\n" + "="*80)
            print("*** THE FLAG ***")
            print("="*80)
            for flag in flags:
                print(flag)
            print("="*80)
        
        exit(0)

print("\nLevel 3 leetspeak didn't work either.")
print("Trying even more aggressive variations...")

# Maybe it's ONLY certain letters?
def custom_leet(text):
    # Try different combinations
    return text.replace('C', '(').replace('c', '(').replace('A','4').replace('a','4').replace('N','|\|').replace('n','|\|')

for base in bases[:3]:
    pwd = custom_leet(base)
    print(f"Trying custom: {pwd}")
    if try_decrypt(pdf_path, pwd):
        print(f"FOUND: {pwd}")
        exit(0)

print("\nStill no match.")
