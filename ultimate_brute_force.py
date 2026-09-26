#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re
import itertools

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

print("Generating comprehensive password list...")
attempts = set()

# 1. All basic combinations
for sep in ["", " ", "_", "-", ".", "|", ":", ";", "/", "\\"]:
    # All uppercase
    attempts.add(sep.join(passwords_list))
    # All lowercase
    attempts.add(sep.join([p.lower() for p in passwords_list]))
    # Title case
    attempts.add(sep.join([p.title() for p in passwords_list]))
    # First letter caps
    attempts.add(sep.join([p.capitalize() for p in passwords_list]))

# 2. Comprehensive leetspeak
def apply_leet(text, level=1):
    result = text
    if level >= 1:
        result = result.replace('A', '4').replace('a', '4')
        result = result.replace('E', '3').replace('e', '3')
        result = result.replace('I', '1').replace('i', '1')
        result = result.replace('O', '0').replace('o', '0')
        result = result.replace('S', '5').replace('s', '5')
        result = result.replace('T', '7').replace('t', '7')
    if level >= 2:
        result = result.replace('B', '8').replace('b', '8')
        result = result.replace('G', '9').replace('g', '9')
        result = result.replace('L', '1').replace('l', '1')
    if level >= 3:
        result = result.replace('C', '(').replace('c', '(')
        result = result.replace('S', '$').replace('s', '$')
        result = result.replace('A', '@').replace('a', '@')
    return result

bases = [
    "".join(passwords_list),
    " ".join(passwords_list),
    "_".join(passwords_list),
    "-".join(passwords_list),
    "".join([p.lower() for p in passwords_list]),
    " ".join([p.lower() for p in passwords_list]),
    "_".join([p.lower() for p in passwords_list]),
]

for base in bases:
    for level in [1, 2, 3]:
        attempts.add(apply_leet(base, level))

# 3. Partial combinations (all subsets)
for r in range(1, 7):
    for combo in itertools.combinations(passwords_list, r):
        attempts.add("".join(combo))
        attempts.add("".join([c.lower() for c in combo]))
        attempts.add(" ".join(combo))
        attempts.add("_".join(combo))

# 4. Reversed
full = "".join(passwords_list)
attempts.add(full[::-1])
attempts.add(full.lower()[::-1])
attempts.add("".join(passwords_list[::-1]))
attempts.add("".join([p.lower() for p in passwords_list[::-1]]))

# 5. First/Last letters
attempts.add("".join([p[0] for p in passwords_list]))
attempts.add("".join([p[0].lower() for p in passwords_list]))
attempts.add("".join([p[-1] for p in passwords_list]))
attempts.add("".join([p[-1].lower() for p in passwords_list]))

# 6. With common prefixes/suffixes
for prefix in ["", "pass", "PASS", "Pass", "flag", "FLAG", "Flag", "key", "KEY", "Key", "password", "PASSWORD"]:
    for suffix in ["", "pass", "PASS", "Pass", "flag", "FLAG", "Flag", "key", "KEY", "Key", "password", "PASSWORD"]:
        if prefix or suffix:
            for base in ["".join(passwords_list), "".join([p.lower() for p in passwords_list])]:
                attempts.add(f"{prefix}{base}{suffix}")
                attempts.add(f"{prefix}_{base}_{suffix}")
                attempts.add(f"{prefix}-{base}-{suffix}")

# 7. Numbers
attempts.add("567363")  # lengths
attempts.add("".join([str(len(p)) for p in passwords_list]))

# 8. ASCII values
attempts.add("".join([str(ord(p[0])) for p in passwords_list]))

# 9. Alternating patterns
alt1 = "".join([p.upper() if i % 2 == 0 else p.lower() for i, p in enumerate(passwords_list)])
alt2 = "".join([p.lower() if i % 2 == 0 else p.upper() for i, p in enumerate(passwords_list)])
attempts.add(alt1)
attempts.add(alt2)

# 10. CamelCase variations
attempts.add("VoiceCannotSilenceButSystemCan")
attempts.add("voiceCannotSilenceButSystemCan")
attempts.add("VoiceCanNotSilenceButSystemCan")

# 11. Special patterns from hint
attempts.add("6casepasswordfragmentsarepass")
attempts.add("6CasePasswordFragmentsArePass")
attempts.add("VOICECANNOTSILENCEBUTSYSTEMCAN6")
attempts.add("6VOICECANNOTSILENCEBUTSYSTEMCAN")

# 12. Just the message
attempts.add("VOICE CANNOT SILENCE BUT SYSTEM CAN")
attempts.add("voice cannot silence but system can")
attempts.add("Voice Cannot Silence But System Can")

# Remove empty strings
attempts.discard("")

print(f"\nTrying {len(attempts)} unique passwords...")
print("="*60)

count = 0
for pwd in sorted(attempts):
    count += 1
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n*** SUCCESS! Password found: {pwd} ***")
        print("\n" + "="*80)
        print("FLAG FILE CONTENT:")
        print("="*80)
        
        full_text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                full_text += text
                print(f"\n--- PAGE {page_num + 1} ---")
                print(text)
            except Exception as e:
                print(f"Error on page {page_num + 1}: {e}")
        
        # Extract flag
        flags = re.findall(r'BPCTF\{[^}]+\}', full_text)
        if flags:
            print("\n" + "="*80)
            print("*** FLAG FOUND ***")
            print("="*80)
            for flag in flags:
                print(flag)
        else:
            print("\nNo BPCTF{} pattern found. Searching for any flag-like pattern...")
            # Try other patterns
            other_flags = re.findall(r'\{[^}]{10,}\}', full_text)
            if other_flags:
                print("Possible flags:")
                for f in other_flags:
                    print(f)
        
        exit(0)
    
    if count % 500 == 0:
        print(f"Tried {count}/{len(attempts)} passwords...")

print(f"\nTried all {len(attempts)} passwords. None worked.")
print("\nThe password must use a different logic or encoding.")
