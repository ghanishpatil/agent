#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re

def try_decrypt(pdf_path, password):
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
passwords = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

print("Case Style Analysis")
print("="*80)
print("Case 1: 'Pascal Case' - PascalCase (each word capitalized, no spaces)")
print("Case 2: 'Shadow Case' - ???")
print("Case 7: 'LeetSpeak Unlo cks' - LeetSpeak with unusual spacing")
print()

# PascalCase: VoiceCannotSilenceButSystemCan
pascal_case = "".join([p.capitalize() for p in passwords])
print(f"PascalCase: {pascal_case}")

# camelCase: voiceCannotSilenceButSystemCan
camel_case = passwords[0].lower() + "".join([p.capitalize() for p in passwords[1:]])
print(f"camelCase: {camel_case}")

# snake_case: voice_cannot_silence_but_system_can
snake_case = "_".join([p.lower() for p in passwords])
print(f"snake_case: {snake_case}")

# SCREAMING_SNAKE_CASE: VOICE_CANNOT_SILENCE_BUT_SYSTEM_CAN
screaming_snake = "_".join(passwords)
print(f"SCREAMING_SNAKE_CASE: {screaming_snake}")

# kebab-case: voice-cannot-silence-but-system-can
kebab_case = "-".join([p.lower() for p in passwords])
print(f"kebab-case: {kebab_case}")

# SCREAMING-KEBAB-CASE: VOICE-CANNOT-SILENCE-BUT-SYSTEM-CAN
screaming_kebab = "-".join(passwords)
print(f"SCREAMING-KEBAB-CASE: {screaming_kebab}")

wordlist = [
    pascal_case,
    camel_case,
    snake_case,
    screaming_snake,
    kebab_case,
    screaming_kebab,
]

# Level 3 leetspeak
def level3_leet(text):
    mapping = {
        'A': '4', 'a': '4', 'B': '8', 'b': '8', 'C': '(', 'c': '(',
        'E': '3', 'e': '3', 'G': '9', 'g': '9', 'I': '1', 'i': '1',
        'L': '1', 'l': '1', 'O': '0', 'o': '0', 'S': '5', 's': '5',
        'T': '7', 't': '7', 'Z': '2', 'z': '2',
    }
    return "".join([mapping.get(c, c) for c in text])

# Apply leetspeak to all
print()
print("With Level 3 Leetspeak:")
print("-"*80)
for style in wordlist:
    leet_version = level3_leet(style)
    print(f"{leet_version}")
    wordlist.append(leet_version)

print()
print(f"Testing {len(wordlist)} case-style passwords...")
print("="*80)

for pwd in wordlist:
    print(f"Trying: {pwd}")
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n{'='*80}")
        print(f"*** PASSWORD FOUND: {pwd} ***")
        print(f"{'='*80}\n")
        
        full_text = ""
        for page_num, page in enumerate(reader.pages, 1):
            try:
                text = page.extract_text()
                full_text += text
                print(f"PAGE {page_num}:")
                print("-"*80)
                print(text)
                print()
            except Exception as e:
                print(f"Error on page {page_num}: {e}")
        
        flags = re.findall(r'BPCTF\{[^}]+\}', full_text)
        if flags:
            print("\n" + "="*80)
            print("*** THE FLAG ***")
            print("="*80)
            for flag in flags:
                print(flag)
            print("="*80)
        
        exit(0)

print("\nCase styles didn't work.")
print()
print("Wait... 'Pascal Case' might be a hint about the PASSWORD itself!")
print("What if we need to apply PascalCase to the HINT text?")
print()

# Try the hint itself in different formats
hint_words = ["LeetSpeak", "Unlocks", "6", "case", "password", "fragments", "are", "pass"]
hint_pascal = "".join([w.capitalize() for w in hint_words])
print(f"Hint in PascalCase: {hint_pascal}")

if try_decrypt(pdf_path, hint_pascal):
    print("FOUND WITH HINT PASCAL!")
    exit(0)

# Try the message
message_words = ["voice", "cannot", "silence", "but", "system", "can"]
message_pascal = "".join([w.capitalize() for w in message_words])
print(f"Message in PascalCase: {message_pascal}")

if try_decrypt(pdf_path, message_pascal):
    print("FOUND WITH MESSAGE PASCAL!")
    exit(0)

print("\nStill searching...")
