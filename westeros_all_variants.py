#!/usr/bin/env python3
"""
Try all possible romanization and case variants
"""

# Part 1: Jo0h5 (could be John Snow in leetspeak?)
part1_variants = ["Jo0h5", "john5", "Johns", "JohnS"]

# Part 2: IR (Bacon cipher from abaaa baaab)
part2_variants = ["IR", "ir", "Is", "is"]

# Part 3: りちししいす
# Different romanization systems:
# Hepburn: ri-chi-shi-shi-i-su
# Kunrei: ri-ti-si-si-i-su  
# Nihon: ri-ti-si-si-i-su

part3_variants = [
    "richishishiisu",  # Standard
    "ritisisiisu",     # Kunrei/Nihon
    "riches",          # Phonetic English?
    "richis",          # Shortened
]

print("Generating all possible flag combinations:\n")
count = 1
for p1 in part1_variants:
    for p2 in part2_variants:
        for p3 in part3_variants:
            flag = f"Kaal{{{p1}_{p2}_{p3}}}"
            print(f"{count:2d}. {flag}")
            count += 1

print(f"\nTotal combinations: {count-1}")
