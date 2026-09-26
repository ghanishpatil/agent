#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import itertools

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

# The 6 passwords
passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

# Generate many variations
attempts = []

# 1. Full phrase variations
full = "".join(passwords_list)
attempts.append(("Full combined", full))
attempts.append(("Full lowercase", full.lower()))

# 2. With spaces
with_spaces = " ".join(passwords_list)
attempts.append(("With spaces", with_spaces))

# 3. Leetspeak mappings
def to_leet(text, mapping):
    result = text
    for old, new in mapping.items():
        result = result.replace(old, new)
    return result

# Different leetspeak mappings
leet_maps = [
    {'A':'4', 'E':'3', 'I':'1', 'O':'0', 'S':'5', 'T':'7'},
    {'A':'@', 'E':'3', 'I':'!', 'O':'0', 'S':'$', 'T':'7'},
    {'A':'4', 'E':'3', 'I':'1', 'O':'0', 'S':'5', 'T':'7', 'B':'8'},
    {'A':'4', 'E':'3', 'I':'1', 'O':'0', 'S':'5', 'T':'7', 'C':'('},
]

for i, lmap in enumerate(leet_maps):
    attempts.append((f"Leet{i+1} full", to_leet(full, lmap)))
    attempts.append((f"Leet{i+1} spaces", to_leet(with_spaces, lmap)))
    attempts.append((f"Leet{i+1} lower", to_leet(full.lower(), lmap)))

# 4. First letters
first_letters = "".join([p[0] for p in passwords_list])
attempts.append(("First letters", first_letters))
for i, lmap in enumerate(leet_maps):
    attempts.append((f"First letters leet{i+1}", to_leet(first_letters, lmap)))

# 5. Last letters
last_letters = "".join([p[-1] for p in passwords_list])
attempts.append(("Last letters", last_letters))

# 6. Alternating
alt1 = "".join([p[0] if i%2==0 else p[-1] for i, p in enumerate(passwords_list)])
attempts.append(("Alternating first/last", alt1))

# 7. Numbers from lengths
lengths = "".join([str(len(p)) for p in passwords_list])
attempts.append(("Lengths", lengths))

# 8. Try reversing
attempts.append(("Reversed full", full[::-1]))
attempts.append(("Reversed phrase", "".join(passwords_list[::-1])))

print(f"Trying {len(attempts)} password combinations...")
print("="*60)

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
                    text = page.extract_text()
                    print(text)
                    
                    import re
                    flags = re.findall(r'BPCTF\{[^}]+\}', text)
                    if flags:
                        print("\n" + "="*80)
                        print("THE FLAG IS:")
                        print("="*80)
                        for flag in flags:
                            print(flag)
                except Exception as e:
                    print(f"Error: {e}")
        break
    else:
        print(f"Failed: {desc:30s} = {pwd}")
else:
    print("\n❌ Still no match. The password logic must be different...")
