#!/usr/bin/env python3
import pikepdf
import re

wordlist = [
    # Challenge name variations
    "TheBleedingPressIndex",
    "thebleedingpressindex",
    "THEBLEEDINGPRESSINDEX",
    "The_Bleeding_Press_Index",
    "the_bleeding_press_index",
    "THE_BLEEDING_PRESS_INDEX",
    "bleeding-press-index",
    "BleedingPressIndex",
    "bleedingpressindex",
    "BLEEDINGPRESSINDEX",
    "BPCTF",
    "bpctf",
    "BPIndex",
    "bpindex",
    # Acronyms
    "TBPI",
    "tbpi",
    "BPI",
    "bpi",
    # With numbers
    "BleedingPress2025",
    "BleedingPress2026",
    "Index2025",
    "Index2026",
    # Leetspeak versions
    "7h38133d1n9Pr355Ind3x",
    "813331N9PR355IND3X",
    "bl33d1ngpr3ss1nd3x",
    # Combined with passwords
    "VOICECANNOTSILENCEBUTSYSTEMCANindex",
    "voicecannotsilencebutsystemcanindex",
    # Republic of Veritas
    "RepublicOfVeritas",
    "republicofveritas",
    "REPUBLICOFVERITAS",
    "Veritas2025",
    "veritas2025",
    # Case-related
    "Case1234567",
    "case1234567",
    "1234567",
    "7654321",
    # Press freedom
    "PressFreedom",
    "pressfreedom",
    "PRESSFREEDOM",
    "press_freedom",
    "PressIndex",
    "pressindex",
    # Transparency
    "TransparencyIndex",
    "transparencyindex",
    # Ministry
    "MinistryOfInformation",
    "ministryofinformation",
    # 13 days
    "13days",
    "thirteendays",
    "ThirteenDays",
    # Seven
    "seven",
    "Seven",
    "SEVEN",
    "7",
]

print(f"Trying {len(wordlist)} challenge-related passwords...")

for pwd in wordlist:
    try:
        with pikepdf.open("Cases/Flag_protected.pdf", password=pwd) as pdf:
            print(f"\n*** PASSWORD FOUND: {pwd} ***\n")
            text = ""
            for page in pdf.pages:
                t = page.extract_text()
                text += t
                print(t)
                print("-"*80)
            
            flags = re.findall(r'BPCTF\{[^}]+\}', text)
            if flags:
                print("\n" + "="*80)
                print("*** THE FLAG ***")
                print("="*80)
                print(flags[0])
                print("="*80)
            exit(0)
    except:
        pass

print("\nNone of the challenge-related passwords worked.")
