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
                result = reader.decrypt(password)
                if result:
                    return reader
    except:
        pass
    return None

pdf_path = Path("Cases/Flag_protected.pdf")
passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

print("Generating MASSIVE password list...")
attempts = set()

# ALL possible separators
separators = ["", " ", "_", "-", ".", ",", ";", ":", "|", "/", "\\", "+", "=", "*", "&", "#", "@", "!", "~"]

# ALL case variations
def all_case_variations(words):
    variations = []
    # All upper
    variations.append([w.upper() for w in words])
    # All lower
    variations.append([w.lower() for w in words])
    # Title
    variations.append([w.title() for w in words])
    # Capitalize
    variations.append([w.capitalize() for w in words])
    # First upper rest lower
    variations.append([w[0].upper() + w[1:].lower() if len(w) > 1 else w.upper() for w in words])
    # Alternating
    for i in range(2**len(words)):
        var = []
        for j, w in enumerate(words):
            if (i >> j) & 1:
                var.append(w.upper())
            else:
                var.append(w.lower())
        variations.append(var)
    return variations

# Generate with all separators and case variations
for sep in separators[:10]:  # Limit to first 10 separators
    for case_var in all_case_variations(passwords_list):
        attempts.add(sep.join(case_var))

# Leetspeak - EVERY possible mapping
def comprehensive_leet(text):
    variations = [text]
    
    # Progressive leetspeak
    leet_maps = [
        {'A': '4', 'E': '3', 'I': '1', 'O': '0', 'S': '5', 'T': '7'},
        {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'},
        {'A': '@', 'E': '3', 'I': '!', 'O': '0', 'S': '$', 'T': '7'},
        {'B': '8', 'G': '9', 'L': '1', 'Z': '2'},
        {'b': '8', 'g': '9', 'l': '1', 'z': '2'},
    ]
    
    for lmap in leet_maps:
        new_text = text
        for old, new in lmap.items():
            new_text = new_text.replace(old, new)
        variations.append(new_text)
    
    return variations

# Apply leetspeak to base combinations
bases = [
    "".join(passwords_list),
    " ".join(passwords_list),
    "_".join(passwords_list),
    "-".join(passwords_list),
    "".join([p.lower() for p in passwords_list]),
    " ".join([p.lower() for p in passwords_list]),
]

for base in bases:
    for leet_var in comprehensive_leet(base):
        attempts.add(leet_var)

# Subsets - try removing one word at a time
for i in range(len(passwords_list)):
    subset = passwords_list[:i] + passwords_list[i+1:]
    attempts.add("".join(subset))
    attempts.add(" ".join(subset))
    attempts.add("_".join(subset))

# Pairs and triples
for r in [2, 3]:
    for combo in itertools.combinations(passwords_list, r):
        attempts.add("".join(combo))
        attempts.add(" ".join(combo))

# With numbers
for i in range(10):
    attempts.add(f"{''.join(passwords_list)}{i}")
    attempts.add(f"{i}{''.join(passwords_list)}")
    attempts.add(f"{''.join([p.lower() for p in passwords_list])}{i}")

# Reversed
attempts.add("".join(passwords_list)[::-1])
attempts.add("".join(passwords_list[::-1]))

# First/last letters with variations
first_letters = "".join([p[0] for p in passwords_list])
last_letters = "".join([p[-1] for p in passwords_list])
for fl in [first_letters, first_letters.lower()]:
    attempts.add(fl)
    for leet_var in comprehensive_leet(fl):
        attempts.add(leet_var)

# Common prefixes/suffixes
for prefix in ["", "flag", "FLAG", "pass", "PASS", "key", "KEY"]:
    for suffix in ["", "flag", "FLAG", "pass", "PASS", "key", "KEY"]:
        if prefix or suffix:
            base = "".join(passwords_list)
            attempts.add(f"{prefix}{base}{suffix}")
            attempts.add(f"{prefix}_{base}_{suffix}")

# The hint itself
attempts.add("6casepasswordfragmentsarepass")
attempts.add("6 case password fragments are pass")

# Remove empty
attempts.discard("")

print(f"\nGenerated {len(attempts)} unique passwords")
print("Starting brute force attack...")
print("="*60)

count = 0
for pwd in sorted(attempts):
    count += 1
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n*** PASSWORD CRACKED: {pwd} ***\n")
        
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
            print("*** THE FLAG ***")
            print("="*80)
            for flag in flags:
                print(flag)
        
        exit(0)
    
    if count % 1000 == 0:
        print(f"Progress: {count}/{len(attempts)} ({count*100//len(attempts)}%)")

print(f"\nExhausted all {len(attempts)} passwords.")
print("The password uses a logic I haven't discovered.")
