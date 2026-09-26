#!/usr/bin/env python3
import PyPDF2

# Extract Case 7 and look for hidden characters
r = PyPDF2.PdfReader(open('Cases/Case - 7_protected.pdf','rb'))
r.decrypt('CAN')

for page_num, page in enumerate(r.pages):
    text = page.extract_text()
    
    # Look for the hints
    if "LeetSpeak" in text or "6 case" in text:
        print(f"Page {page_num + 1}:")
        print("="*80)
        
        lines = text.split('\n')
        for line in lines:
            if "LeetSpeak" in line or "6 case" in line or "fragments" in line:
                print(f"Line: {repr(line)}")
                print(f"Bytes: {line.encode('utf-8')}")
                print(f"Hex: {line.encode('utf-8').hex()}")
                print()

print("\n" + "="*80)
print("Analysis:")
print("="*80)
print("'LeetSpeak Unlo cks' has a space in 'Unlo cks'")
print("'6 case password  fragments are pass' has double space between 'password' and 'fragments'")
print("\nMaybe the password contains these unusual spacings?")

# Try passwords with unusual spacing
import PyPDF2
from pathlib import Path

def try_pwd(pwd):
    try:
        with open("Cases/Flag_protected.pdf", 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                if reader.decrypt(pwd):
                    return True
    except:
        pass
    return False

attempts = [
    "LeetSpeak Unlo cks",
    "LeetSpeakUnlo cks",
    "LeetSpeakUnlocks",
    "leetspeak unlo cks",
    "l337sp34k unl0 cks",
    "L337SP34K UNL0 CKS",
    
    # With the double space
    "VOICE CANNOT  SILENCE BUT  SYSTEM CAN",
    "voice cannot  silence but  system can",
    
    # Maybe it's telling us to unlock with leetspeak?
    "unlo cks",
    "unlocks",
    "UNLOCKS",
    "UNL0CKS",
    "unl0cks",
]

print("\nTrying passwords with unusual spacing...")
for pwd in attempts:
    if try_pwd(pwd):
        print(f"\nFOUND: {pwd}")
        break
    print(f"No: {repr(pwd)}")
