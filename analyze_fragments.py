#!/usr/bin/env python3
import PyPDF2
from pathlib import Path

def try_password(pdf_path, password):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                result = reader.decrypt(password)
                if result:
                    return True
    except:
        pass
    return False

pdf_path = Path("Cases/Flag_protected.pdf")

# The 6 passwords from cases 2-7
passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

print("Analyzing password fragments...")
print("="*60)
print("Passwords:", passwords_list)
print()

# Try different fragment interpretations
attempts = []

# First letter of each
attempts.append(("First letters", "".join([p[0] for p in passwords_list])))

# Last letter of each
attempts.append(("Last letters", "".join([p[-1] for p in passwords_list])))

# First 2 letters of each
attempts.append(("First 2 letters", "".join([p[:2] for p in passwords_list])))

# First 3 letters of each
attempts.append(("First 3 letters", "".join([p[:3] for p in passwords_list])))

# Middle letter of each
attempts.append(("Middle letters", "".join([p[len(p)//2] for p in passwords_list])))

# Alternating letters
attempts.append(("Alt letters (even)", "".join([p[i] for p in passwords_list for i in range(0, len(p), 2)])))

# Length of each password as numbers
attempts.append(("Lengths", "".join([str(len(p)) for p in passwords_list])))

# Try leetspeak on combinations
def to_leet(text):
    leet = {'A':'4','E':'3','I':'1','O':'0','S':'5','T':'7','a':'4','e':'3','i':'1','o':'0','s':'5','t':'7'}
    return "".join([leet.get(c, c) for c in text])

for desc, pwd in attempts[:]:
    attempts.append((f"{desc} (leet)", to_leet(pwd)))
    attempts.append((f"{desc} (lower)", pwd.lower()))
    attempts.append((f"{desc} (leet+lower)", to_leet(pwd.lower())))

print(f"Trying {len(attempts)} combinations...")
print()

for desc, pwd in attempts:
    if try_password(pdf_path, pwd):
        print(f"\nSUCCESS! {desc}: {pwd}")
        
        # Extract flag
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            reader.decrypt(pwd)
            
            print("\n" + "="*80)
            print("FLAG CONTENT:")
            print("="*80)
            
            for page in reader.pages:
                try:
                    print(page.extract_text())
                except Exception as e:
                    print(f"Error: {e}")
        break
    else:
        print(f"Failed: {desc:30s} = {pwd}")
else:
    print("\nStill no match. Need to think differently...")
