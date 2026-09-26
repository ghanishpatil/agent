#!/usr/bin/env python3
import itertools

passwords_list = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

print("Generating massive wordlist...")
wordlist = set()

# 1. All permutations of all lengths
print("Adding permutations...")
for r in range(1, 7):
    for perm in itertools.permutations(passwords_list, r):
        # No separator
        wordlist.add("".join(perm))
        # With space
        wordlist.add(" ".join(perm))
        # With underscore
        wordlist.add("_".join(perm))
        # With hyphen
        wordlist.add("-".join(perm))
        
        # Lowercase versions
        wordlist.add("".join([p.lower() for p in perm]))
        wordlist.add(" ".join([p.lower() for p in perm]))

# 2. All combinations (not permutations)
print("Adding combinations...")
for r in range(1, 7):
    for combo in itertools.combinations(passwords_list, r):
        wordlist.add("".join(combo))
        wordlist.add(" ".join(combo))
        wordlist.add("_".join(combo))
        wordlist.add("".join([c.lower() for c in combo]))

# 3. Leetspeak on common ones
print("Adding leetspeak...")
def leet(text):
    return text.replace('A','4').replace('a','4').replace('E','3').replace('e','3').replace('I','1').replace('i','1').replace('O','0').replace('o','0').replace('S','5').replace('s','5').replace('T','7').replace('t','7')

common = [
    "".join(passwords_list),
    " ".join(passwords_list),
    "_".join(passwords_list),
    "-".join(passwords_list),
]

for pwd in common:
    wordlist.add(leet(pwd))
    wordlist.add(leet(pwd.lower()))

# 4. With numbers
print("Adding number variations...")
for i in range(10):
    for pwd in common:
        wordlist.add(f"{pwd}{i}")
        wordlist.add(f"{i}{pwd}")

# 5. Challenge specific
wordlist.update([
    "bleedingpress", "BleedingPress", "BLEEDINGPRESS",
    "bleeding_press", "bleeding-press",
    "veritas", "Veritas", "VERITAS",
    "flag", "FLAG", "password", "PASSWORD",
    "TheBleedingPressIndex",
    "6casepasswordfragmentsarepass",
])

# Save
print(f"\nSaving {len(wordlist)} passwords to mega_wordlist.txt...")
with open("mega_wordlist.txt", "w") as f:
    for pwd in sorted(wordlist):
        f.write(pwd + "\n")

print("Done!")
print(f"Total passwords: {len(wordlist)}")
