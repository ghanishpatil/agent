#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re
import string

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

# CTF-specific password patterns
attempts = []

# 1. Common CTF passwords
common_ctf = [
    "flag", "FLAG", "Flag",
    "password", "PASSWORD", "Password",
    "admin", "ADMIN", "Admin",
    "root", "ROOT", "Root",
    "ctf", "CTF", "Ctf",
    "challenge", "CHALLENGE", "Challenge",
    "secret", "SECRET", "Secret",
    "key", "KEY", "Key",
    "unlock", "UNLOCK", "Unlock",
]
attempts.extend(common_ctf)

# 2. Challenge-specific
challenge_specific = [
    "bleedingpress", "BleedingPress", "BLEEDINGPRESS",
    "bleeding_press", "Bleeding_Press", "BLEEDING_PRESS",
    "bleeding-press", "Bleeding-Press", "BLEEDING-PRESS",
    "veritas", "Veritas", "VERITAS",
    "republic", "Republic", "REPUBLIC",
    "republicofveritas", "RepublicOfVeritas", "REPUBLICOFVERITAS",
    "press", "Press", "PRESS",
    "pressfreedom", "PressFreedom", "PRESSFREEDOM",
    "freedom", "Freedom", "FREEDOM",
    "journalist", "Journalist", "JOURNALIST",
    "transparency", "Transparency", "TRANSPARENCY",
]
attempts.extend(challenge_specific)

# 3. The passwords we found
passwords_found = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

# Try each individually
attempts.extend(passwords_found)
attempts.extend([p.lower() for p in passwords_found])

# Try pairs
for i in range(len(passwords_found)):
    for j in range(i+1, len(passwords_found)):
        attempts.append(passwords_found[i] + passwords_found[j])
        attempts.append(passwords_found[i].lower() + passwords_found[j].lower())
        attempts.append(passwords_found[i] + " " + passwords_found[j])

# 4. Numbers and combinations
for num in range(0, 10):
    attempts.append(str(num))
    attempts.append(f"flag{num}")
    attempts.append(f"FLAG{num}")
    attempts.append(f"password{num}")
    attempts.append(f"PASSWORD{num}")

# 5. Years
for year in [2023, 2024, 2025, 2026]:
    attempts.append(str(year))
    attempts.append(f"flag{year}")
    attempts.append(f"FLAG{year}")

# 6. Common patterns
patterns = [
    "123456", "password123", "admin123",
    "qwerty", "letmein", "welcome",
    "abc123", "password1", "12345678",
]
attempts.extend(patterns)

# 7. Based on the hint structure
hint_based = [
    "6fragments",
    "sixfragments",
    "SixFragments",
    "6Fragments",
    "fragments6",
    "Fragments6",
]
attempts.extend(hint_based)

# Remove duplicates
attempts = list(dict.fromkeys(attempts))

print(f"Trying {len(attempts)} CTF-style passwords...")
print("="*60)

for i, pwd in enumerate(attempts):
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n*** PASSWORD FOUND: {pwd} ***\n")
        
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
            print("*** FLAG ***")
            print("="*80)
            for flag in flags:
                print(flag)
        
        exit(0)
    
    if (i + 1) % 50 == 0:
        print(f"Tried {i + 1}/{len(attempts)}...")

print(f"\nTried all {len(attempts)} passwords. None worked.")
