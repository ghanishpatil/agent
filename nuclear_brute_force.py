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
passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

print("NUCLEAR OPTION: Generating EVERY possible variation...")
attempts = set()

# Every possible character substitution for leetspeak
leet_chars = {
    'A': ['A', 'a', '4', '@'],
    'B': ['B', 'b', '8'],
    'C': ['C', 'c', '(', '<'],
    'E': ['E', 'e', '3'],
    'G': ['G', 'g', '9'],
    'I': ['I', 'i', '1', '!', '|'],
    'L': ['L', 'l', '1', '|'],
    'O': ['O', 'o', '0'],
    'S': ['S', 's', '5', '$'],
    'T': ['T', 't', '7', '+'],
    'Z': ['Z', 'z', '2'],
}

# Generate base strings
bases = []
for sep in ['', ' ', '_', '-']:
    bases.append(sep.join(passwords_list))
    bases.append(sep.join([p.lower() for p in passwords_list]))
    bases.append(sep.join([p.upper() for p in passwords_list]))

# For each base, try EVERY leet variation (limited to first few chars to avoid explosion)
for base in bases[:5]:  # Limit bases
    # Try standard leetspeak
    leet1 = base
    for char, replacements in leet_chars.items():
        if char in leet1:
            for repl in replacements[1:2]:  # Just first replacement
                attempts.add(leet1.replace(char, repl))
                attempts.add(leet1.replace(char.lower(), repl))

# Add every combination we've tried before
# Comprehensive list
mega_list = [
    # Basic
    "VOICECANNOTSILENCEBUTSYSTEMCAN",
    "voicecannotsilencebutsystemcan",
    "VoiceCannotSilenceButSystemCan",
    
    # Standard leet
    "V01C3C4NN0751L3NC3BU75Y573MC4N",
    "v01c3c4nn0751l3nc3bu75y573mc4n",
    
    # With spaces
    "VOICE CANNOT SILENCE BUT SYSTEM CAN",
    "voice cannot silence but system can",
    "V01C3 C4NN07 51L3NC3 BU7 5Y573M C4N",
    
    # Underscores
    "VOICE_CANNOT_SILENCE_BUT_SYSTEM_CAN",
    "voice_cannot_silence_but_system_can",
    "V01C3_C4NN07_51L3NC3_BU7_5Y573M_C4N",
    
    # Hyphens
    "VOICE-CANNOT-SILENCE-BUT-SYSTEM-CAN",
    "voice-cannot-silence-but-system-can",
    "V01C3-C4NN07-51L3NC3-BU7-5Y573M-C4N",
    
    # Dots
    "VOICE.CANNOT.SILENCE.BUT.SYSTEM.CAN",
    "voice.cannot.silence.but.system.can",
    
    # Mixed case
    "VoIcEcAnNoTsIlEnCeBuTsYsTeM cAn",
    "vOiCeCaNnOtSiLe NcEbUtSyStEmCaN",
]

attempts.update(mega_list)

# Try with numbers
for i in range(10):
    attempts.add(f"VOICECANNOTSILENCEBUTSYSTEMCAN{i}")
    attempts.add(f"{i}VOICECANNOTSILENCEBUTSYSTEMCAN")
    attempts.add(f"V01C3C4NN0751L3NC3BU75Y573MC4N{i}")

# Try reversed
attempts.add("NACMETSYSTUBECNELISTONNACECIOV")
attempts.add("nacmetsystubecnelistonnaceciov")

# Try just parts
for word in passwords_list:
    attempts.add(word)
    attempts.add(word.lower())
    attempts.add(word.replace('A','4').replace('E','3').replace('I','1').replace('O','0').replace('S','5').replace('T','7'))

print(f"\nTrying {len(attempts)} passwords with progress updates...")
print("="*80)

count = 0
for pwd in sorted(attempts):
    count += 1
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n\n*** PASSWORD CRACKED: '{pwd}' ***\n")
        
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
        else:
            print("\nSearching for any flag pattern...")
            all_flags = re.findall(r'\{[^}]+\}', full_text)
            if all_flags:
                for f in all_flags:
                    print(f"Possible: {f}")
        
        exit(0)
    
    if count % 100 == 0:
        print(f"[{count}/{len(attempts)}] Still trying...")

print(f"\nExhausted all {len(attempts)} attempts.")
print("The password is not in my generated list.")
