#!/usr/bin/env python3
import pikepdf
import re
import itertools

pdf_path = "Cases/Flag_protected.pdf"

# Base passwords from cases
base = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]
full = "VOICECANNOTSILENCEBUTSYSTEMCAN"

wordlist = []

# 1. Basic variations
wordlist.extend([
    full,
    full.lower(),
    "VoiceCannotSilenceButSystemCan",
    "voiceCannotSilenceButSystemCan",
])

# 2. With separators
for sep in ["", " ", "_", "-", "."]:
    wordlist.append(sep.join(base))
    wordlist.append(sep.join([w.lower() for w in base]))
    wordlist.append(sep.join([w.capitalize() for w in base]))

# 3. Leetspeak
leet = {'A':'4','E':'3','I':'1','O':'0','S':'5','T':'7','B':'8','C':'('}
for text in [full, full.lower()]:
    result = text
    for old, new in leet.items():
        result = result.replace(old, new)
    wordlist.append(result)

# 4. Initials
wordlist.extend([
    "".join([w[0] for w in base]),
    "".join([w[0].lower() for w in base]),
    "".join([w[-1] for w in base]),
])

# 5. CTF common
wordlist.extend([
    "bleedingpress", "BleedingPress", "bleeding_press",
    "veritas", "Veritas", "VERITAS",
    "transparency", "Transparency",
    "freedom", "pressfreedom",
    "case7", "CASE7",
    "123456", "password", "admin",
])

# 6. With pass prefix/suffix
for w in [full, full.lower()]:
    wordlist.extend([f"pass{w}", f"{w}pass", f"PASS{w}", f"{w}PASS"])

# 7. Reversed
wordlist.append(full[::-1])
wordlist.append(full.lower()[::-1])

# Remove duplicates
wordlist = list(dict.fromkeys(wordlist))

print(f"Attempting {len(wordlist)} passwords...")
print("="*60)

for i, pwd in enumerate(wordlist, 1):
    try:
        with pikepdf.open(pdf_path, password=pwd) as pdf:
            print(f"\n{'='*80}")
            print(f"SUCCESS! Password: {pwd}")
            print("="*80)
            
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                text += page_text
                print(page_text)
            
            flags = re.findall(r'BPCTF\{[^}]+\}', text)
            if flags:
                print("\n" + "="*80)
                print(f"FLAG: {flags[0]}")
                print("="*80)
            exit(0)
    except:
        pass
    
    if i % 100 == 0:
        print(f"Tried {i}...")

print("\nStandard wordlist exhausted. Trying numeric brute force...")
for num in range(1000000):
    if num % 50000 == 0:
        print(f"Trying {num}...")
    try:
        with pikepdf.open(pdf_path, password=str(num)) as pdf:
            print(f"\nSUCCESS! Password: {num}")
            exit(0)
    except:
        pass

print("No password found.")
