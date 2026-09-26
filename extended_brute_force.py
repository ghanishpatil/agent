#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re
import itertools

def try_password(pdf_path, password):
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

passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

# Extended attempts
attempts = set()

# 1. All case variations
for case_func in [str.upper, str.lower, str.title]:
    full = "".join([case_func(p) for p in passwords_list])
    attempts.add(full)
    attempts.add(" ".join([case_func(p) for p in passwords_list]))

# 2. Comprehensive leetspeak
def apply_leet(text, aggressive=False):
    mappings = {
        'A': '4', 'a': '4',
        'E': '3', 'e': '3',
        'I': '1', 'i': '1',
        'O': '0', 'o': '0',
        'S': '5', 's': '5',
        'T': '7', 't': '7',
    }
    if aggressive:
        mappings.update({
            'B': '8', 'b': '8',
            'C': '(', 'c': '(',
            'G': '9', 'g': '9',
            'L': '1', 'l': '1',
        })
    result = text
    for old, new in mappings.items():
        result = result.replace(old, new)
    return result

bases = [
    "".join(passwords_list),
    " ".join(passwords_list),
    "".join([p.lower() for p in passwords_list]),
    " ".join([p.lower() for p in passwords_list]),
    "VoiceCannotSilenceButSystemCan",
    "Voice Cannot Silence But System Can",
]

for base in bases:
    attempts.add(apply_leet(base, False))
    attempts.add(apply_leet(base, True))

# 3. Partial combinations
for r in range(2, 7):
    for combo in itertools.combinations(passwords_list, r):
        attempts.add("".join(combo))
        attempts.add("".join([c.lower() for c in combo]))

# 4. With common prefixes/suffixes
for prefix in ["", "pass", "PASS", "flag", "FLAG", "key", "KEY"]:
    for suffix in ["", "pass", "PASS", "flag", "FLAG", "key", "KEY"]:
        if prefix or suffix:
            base = "".join(passwords_list)
            attempts.add(f"{prefix}{base}{suffix}")
            attempts.add(f"{prefix}{base.lower()}{suffix}")

# 5. Acronyms and initials
attempts.add("".join([p[0] for p in passwords_list]))  # VCSBSC
attempts.add("".join([p[0].lower() for p in passwords_list]))  # vcsbsc
attempts.add("".join([p[-1] for p in passwords_list]))  # ETETMN

# 6. Numbers
attempts.add("567363")  # lengths
attempts.add("".join([str(ord(p[0])) for p in passwords_list]))  # ASCII values

# 7. Special patterns
attempts.add("Voice_Cannot_Silence_But_System_Can")
attempts.add("voice-cannot-silence-but-system-can")
attempts.add("VOICE.CANNOT.SILENCE.BUT.SYSTEM.CAN")

print(f"Trying {len(attempts)} unique passwords...")
print("="*60)

for i, pwd in enumerate(sorted(attempts)):
    reader = try_password(pdf_path, pwd)
    if reader:
        print(f"\nSUCCESS! Password: {pwd}")
        print("\n" + "="*80)
        print("FLAG CONTENT:")
        print("="*80)
        
        for page in reader.pages:
            try:
                text = page.extract_text()
                print(text)
                
                flags = re.findall(r'BPCTF\{[^}]+\}', text)
                if flags:
                    print("\n" + "="*80)
                    print("THE FLAG:")
                    print("="*80)
                    for flag in flags:
                        print(flag)
                        return
            except Exception as e:
                print(f"Error: {e}")
        return
    
    if (i + 1) % 100 == 0:
        print(f"Tried {i + 1}/{len(attempts)} passwords...")

print("\nNo match found. Trying even more variations...")

# Last resort - try every possible separator and case combination
for sep in ["", " ", "_", "-", ".", "|", ":", ";"]:
    for case_pattern in ["UPPER", "lower", "Title", "aLtErNaTe"]:
        if case_pattern == "UPPER":
            pwd = sep.join([p.upper() for p in passwords_list])
        elif case_pattern == "lower":
            pwd = sep.join([p.lower() for p in passwords_list])
        elif case_pattern == "Title":
            pwd = sep.join([p.title() for p in passwords_list])
        else:  # alternate
            pwd = sep.join([p.upper() if i % 2 == 0 else p.lower() for i, p in enumerate(passwords_list)])
        
        reader = try_password(pdf_path, pwd)
        if reader:
            print(f"\nFOUND IT! Password: {pwd}")
            for page in reader.pages:
                text = page.extract_text()
                print(text)
                flags = re.findall(r'BPCTF\{[^}]+\}', text)
                if flags:
                    for flag in flags:
                        print(f"\nFLAG: {flag}")
                        return

print("\nStill no match. The password must use a different logic.")
