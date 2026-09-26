#!/usr/bin/env python3
import pikepdf
import itertools
import string

pdf_path = "Cases/Flag_protected.pdf"

# Base message
words = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]
base = "".join(words)

# Comprehensive leetspeak mappings
leet_maps = {
    'A': ['A', 'a', '4', '@'],
    'B': ['B', 'b', '8'],
    'C': ['C', 'c', '(', '<'],
    'E': ['E', 'e', '3'],
    'I': ['I', 'i', '1', '!', '|'],
    'O': ['O', 'o', '0'],
    'S': ['S', 's', '5', '$'],
    'T': ['T', 't', '7', '+'],
    'N': ['N', 'n'],
    'V': ['V', 'v'],
    'L': ['L', 'l', '1'],
    'M': ['M', 'm'],
    'U': ['U', 'u'],
    'Y': ['Y', 'y'],
}

def generate_leet_variations(text, max_variations=10000):
    """Generate leetspeak variations"""
    variations = set()
    
    # Get positions of letters that can be leeted
    leet_positions = []
    for i, char in enumerate(text):
        if char.upper() in leet_maps:
            leet_positions.append(i)
    
    # Try different combinations
    for num_changes in range(1, min(len(leet_positions) + 1, 8)):
        for positions in itertools.combinations(leet_positions, num_changes):
            variant = list(text)
            for pos in positions:
                char = text[pos].upper()
                if char in leet_maps:
                    # Use most common leet substitution
                    if char == 'A': variant[pos] = '4'
                    elif char == 'E': variant[pos] = '3'
                    elif char == 'I': variant[pos] = '1'
                    elif char == 'O': variant[pos] = '0'
                    elif char == 'S': variant[pos] = '5'
                    elif char == 'T': variant[pos] = '7'
                    elif char == 'B': variant[pos] = '8'
                    elif char == 'C': variant[pos] = '('
            variations.add(''.join(variant))
            
            if len(variations) >= max_variations:
                return list(variations)
    
    return list(variations)

# Generate wordlist
wordlist = []

# 1. Basic forms
wordlist.extend([
    base,
    base.lower(),
    base.capitalize(),
    "VoiceCannotSilenceButSystemCan",
    "voiceCannotSilenceButSystemCan",
])

# 2. With separators
for sep in ["", " ", "_", "-", "."]:
    wordlist.append(sep.join(words))
    wordlist.append(sep.join([w.lower() for w in words]))
    wordlist.append(sep.join([w.capitalize() for w in words]))

# 3. Generate leetspeak variations
print("Generating leetspeak variations...")
for base_text in [base, base.lower()]:
    leet_vars = generate_leet_variations(base_text, max_variations=5000)
    wordlist.extend(leet_vars)
    print(f"Generated {len(leet_vars)} variations for '{base_text[:20]}...'")

# 4. With common prefixes/suffixes
for prefix in ["", "pass", "PASS", "flag", "FLAG"]:
    for suffix in ["", "pass", "PASS", "flag", "FLAG", "123", "!"]:
        if prefix or suffix:
            wordlist.append(f"{prefix}{base}{suffix}")
            wordlist.append(f"{prefix}{base.lower()}{suffix}")

# 5. Reversed
wordlist.append(base[::-1])
wordlist.append(base.lower()[::-1])

# 6. Initials
wordlist.extend([
    "".join([w[0] for w in words]),
    "".join([w[0].lower() for w in words]),
    "".join([w[-1] for w in words]),
])

# 7. CTF common patterns
wordlist.extend([
    "bleedingpress", "BleedingPress", "BLEEDINGPRESS",
    "veritas", "Veritas", "VERITAS",
    "transparency", "freedom", "stability",
    "13days", "sevencases", "7cases",
])

# Remove duplicates
wordlist = list(dict.fromkeys(wordlist))

print(f"\nTotal passwords to try: {len(wordlist)}")
print("="*60)
print("Starting crack attempt...")

for i, pwd in enumerate(wordlist, 1):
    try:
        with pikepdf.open(pdf_path, password=pwd) as pdf:
            print(f"\n{'='*80}")
            print(f"SUCCESS! Password found: {pwd}")
            print("="*80)
            
            text = ""
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                text += page_text
                print(f"\n--- PAGE {page_num} ---")
                print(page_text)
            
            import re
            flags = re.findall(r'BPCTF\{[^}]+\}', text)
            if flags:
                print("\n" + "="*80)
                print(f"FLAG FOUND: {flags[0]}")
                print("="*80)
            
            # Save to file
            with open("FLAG_RESULT.txt", "w") as f:
                f.write(f"Password: {pwd}\n")
                f.write(f"{'='*80}\n")
                f.write(text)
                if flags:
                    f.write(f"\n\nFLAG: {flags[0]}\n")
            
            exit(0)
    except:
        pass
    
    if i % 500 == 0:
        print(f"Tried {i}/{len(wordlist)} passwords...")

print("\nPassword not found in generated wordlist.")
print("The password might require a different pattern.")
