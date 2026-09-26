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

# The hint says "6 case password fragments are pass"
# Maybe it means the passwords ARE the passphrase, or "pass" is key

passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

attempts = [
    # Maybe just "pass"?
    "pass",
    "PASS",
    "Pass",
    
    # Or the fragments themselves?
    "fragments",
    "FRAGMENTS",
    "Fragments",
    
    # Or "are pass"?
    "arepass",
    "AREPASS",
    "are pass",
    "ARE PASS",
    
    # The whole hint?
    "6casepasswordfragmentsarepass",
    "6 case password fragments are pass",
    "6CasePasswordFragmentsArePass",
    
    # Maybe it's telling us the format?
    "VOICE-CANNOT-SILENCE-BUT-SYSTEM-CAN",
    "Voice-Cannot-Silence-But-System-Can",
    
    # Or maybe concatenate with "pass"?
    "VOICECANNOTSILENCEBUTSYSTEMCANPASS",
    "passVOICECANNOTSILENCEBUTSYSTEMCAN",
    
    # Try the 6 passwords as individual words
    "VOICE",
    "CANNOT", 
    "SILENCE",
    "BUT",
    "SYSTEM",
    "CAN",
    
    # Maybe it's about the NUMBER 6?
    "6",
    "six",
    "SIX",
    
    # Or combining 6 with the message?
    "6VOICECANNOTSILENCEBUTSYSTEMCAN",
    "VOICECANNOTSILENCEBUTSYSTEMCAN6",
    
    # Leetspeak "pass"
    "p455",
    "P455",
    "p@55",
    "P@55",
]

print(f"Trying {len(attempts)} password variations...")
print("="*60)

for pwd in attempts:
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n*** SUCCESS! Password: {pwd} ***\n")
        
        full_text = ""
        for page in reader.pages:
            try:
                text = page.extract_text()
                full_text += text
                print(text)
            except Exception as e:
                print(f"Error: {e}")
        
        flags = re.findall(r'BPCTF\{[^}]+\}', full_text)
        if flags:
            print("\n" + "="*80)
            print("FLAG:")
            print("="*80)
            for flag in flags:
                print(flag)
        
        exit(0)
    else:
        print(f"Failed: {pwd}")

print("\nNone of these worked either.")
