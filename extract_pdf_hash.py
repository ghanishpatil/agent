#!/usr/bin/env python3
"""
Extract PDF encryption info to create a custom wordlist attack
"""
import pikepdf
from pathlib import Path

pdf_path = Path("Cases/Flag_protected.pdf")

print("Extracting PDF encryption information...")
print("="*80)

try:
    # Try to get encryption info
    with pikepdf.open(pdf_path, password="", allow_overwriting_input=True) as pdf:
        print("PDF opened with empty password!")
except pikepdf.PasswordError as e:
    print(f"Password protected: {e}")
    print("\nAttempting to extract encryption metadata...")
    
    # Read raw PDF to get encryption info
    with open(pdf_path, 'rb') as f:
        content = f.read()
        
        # Look for encryption dictionary
        if b'/Encrypt' in content:
            print("Found /Encrypt dictionary")
            
            # Extract encryption info
            import re
            
            # Look for encryption parameters
            encrypt_match = re.search(b'/Encrypt.*?/Filter.*?/Standard', content)
            if encrypt_match:
                print(f"Encryption type: Standard")
            
            # Look for key length
            length_match = re.search(b'/Length\s+(\d+)', content)
            if length_match:
                key_length = int(length_match.group(1))
                print(f"Key length: {key_length} bits")
            
            # Look for revision
            r_match = re.search(b'/R\s+(\d+)', content)
            if r_match:
                revision = int(r_match.group(1))
                print(f"Revision: {revision}")
            
            # Look for permissions
            p_match = re.search(b'/P\s+(-?\d+)', content)
            if p_match:
                permissions = int(p_match.group(1))
                print(f"Permissions: {permissions}")

print("\n" + "="*80)
print("Creating custom wordlist from discovered passwords...")
print("="*80)

# Create a comprehensive wordlist
passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

wordlist = []

# Add all basic combinations
for sep in ["", " ", "_", "-", "."]:
    wordlist.append(sep.join(passwords_list))
    wordlist.append(sep.join([p.lower() for p in passwords_list]))
    wordlist.append(sep.join([p.title() for p in passwords_list]))

# Add leetspeak
def leet(text):
    return text.replace('A','4').replace('a','4').replace('E','3').replace('e','3').replace('I','1').replace('i','1').replace('O','0').replace('o','0').replace('S','5').replace('s','5').replace('T','7').replace('t','7')

for pwd in wordlist[:]:
    wordlist.append(leet(pwd))

# Add individual words
wordlist.extend(passwords_list)
wordlist.extend([p.lower() for p in passwords_list])

# Add challenge-specific
wordlist.extend([
    "bleedingpress", "BleedingPress", "BLEEDINGPRESS",
    "veritas", "Veritas", "VERITAS",
    "flag", "FLAG", "password", "PASSWORD",
])

# Save to file
with open("custom_wordlist.txt", "w") as f:
    for pwd in set(wordlist):
        f.write(pwd + "\n")

print(f"Created custom_wordlist.txt with {len(set(wordlist))} passwords")
print("\nNow attempting dictionary attack...")
