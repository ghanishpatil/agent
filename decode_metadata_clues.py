#!/usr/bin/env python3
"""
Decode the metadata clues found in the PDFs
"""

import pikepdf

print("="*80)
print("DECODING METADATA CLUES")
print("="*80)

# Case 4: Keywords: 66 85 84
print("\n[CASE 4 - Keywords: 66 85 84]")
ascii_codes = [66, 85, 84]
decoded = ''.join([chr(code) for code in ascii_codes])
print(f"ASCII Decode: {decoded}")
print(f"This spells: '{decoded}' - which is one of our fragments!")

# Case 7: Subject: "Encoded LeetSpeak", Keywords: "Level - 3"
print("\n[CASE 7 - Subject: 'Encoded LeetSpeak', Keywords: 'Level - 3']")
print("This suggests:")
print("- LeetSpeak encoding")
print("- Level 3 complexity")
print("- Level 3 leetspeak = AGGRESSIVE substitution")

print("\n" + "="*80)
print("LEVEL 3 LEETSPEAK RULES:")
print("="*80)

print("""
Level 1 (Basic): A=4, E=3, I=1, O=0, S=5, T=7
Level 2 (Medium): + B=8, C=(, L=1, G=9
Level 3 (Aggressive): ALL possible substitutions

Level 3 Mappings:
A → 4, @, ^, /\
B → 8, |3, ß
C → (, <, {, [
E → 3, €, &
I → 1, !, |, ][
L → 1, |, |_
O → 0, (), []
S → 5, $, §
T → 7, +, †
V → \/, \\//
N → |\\|, /\\/
U → |_|, (_)
Y → ¥, `/
""")

# Try Level 3 leetspeak
base = "VOICECANNOTSILENCEBUTSYSTEMCAN"

print("\n" + "="*80)
print("TRYING LEVEL 3 LEETSPEAK VARIATIONS:")
print("="*80)

level3_attempts = [
    # Aggressive substitutions
    "\\/0!C3C@NN07S!L3NC38U7SYS73MC@N",
    "\\/01C3C4NN075!13NC38U75Y573MC4N",
    "V0!C3(4NN07$!13N(38U7$Y$73M(4N",
    "\\/01(3(4NN07$1L3N(38U7$Y$73M(4N",
    
    # With special characters
    "V0!C3_C@NN07_$!L3NC3_8U7_$Y$73M_C@N",
    "\\/01C3 C4NN07 $1L3NC3 8U7 $Y$73M C4N",
    
    # Mixed case with level 3
    "v0!c3c@nn07$!l3nc38u7$y$73mc@n",
    "V0!c3C@nn07S!l3nc38u7Sy$73mC@n",
]

pdf_path = "Cases/Flag_protected.pdf"

for pwd in level3_attempts:
    try:
        with pikepdf.open(pdf_path, password=pwd) as pdf:
            print(f"\n{'='*80}")
            print(f"🎉 SUCCESS! PASSWORD: {pwd}")
            print("="*80)
            
            text = ""
            for page in pdf.pages:
                t = page.extract_text()
                text += t
                print(t)
            
            import re
            flags = re.findall(r'BPCTF\{[^}]+\}', text)
            if flags:
                print(f"\n{'='*80}")
                print(f"FLAG: {flags[0]}")
                print("="*80)
            
            with open("FLAG_RESULT.txt", "w", encoding="utf-8") as f:
                f.write(f"Password: {pwd}\n{'='*80}\n{text}\n")
                if flags:
                    f.write(f"\nFLAG: {flags[0]}\n")
            
            exit(0)
    except:
        pass

print("\nLevel 3 variations didn't work either.")
print("\nThe hash CANNOT be decoded mathematically.")
print("You MUST use hashcat or find the exact password pattern.")
print("\nSummary:")
print("- Hash = Encrypted data (one-way)")
print("- Password ≠ Inside the hash")
print("- Only solution = Try passwords (brute force)")
