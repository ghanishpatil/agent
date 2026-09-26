#!/usr/bin/env python3
"""
Try all possible middle words for the corrupted flag
"""

# Pattern: Kaal{l4yers_of_d3c03pt10n_m????_@sk_7h3_pr353nc3_0f_pO1s0ns}
# or: Kaal{l4yers_of_d3c03pt10n_m????_m@sk_7h3_pr353nc3_0f_pO1s0ns}

# Theme: whispers, silence, sparse, chord, alignment, final

possible_words = [
    # From Spider challenge
    "@sk",
    
    # Whisper theme
    "wh1sp3r",
    "wh1sp3rs",
    "urm ur",
    "urm0r",
    "urm0rs",
    
    # Silence theme  
    "ut3",
    "ut3d",
    
    # Sparse theme
    "1n1m4l",
    "1n1m1z3",
    
    # Chord theme
    "us1c",
    "3l0dy",
    
    # Alignment theme
    "4tch",
    "4tch3d",
    
    # Final theme
    "0rt4l",
    "0rt4l1ty",
    
    # Mystery theme
    "yst3ry",
    "yst1c",
    "yst1qu3",
    "yst3r13s",
    "yst1f1c4t10n",
    
    # Other possibilities
    "4gn3t1sm",
    "4l1gn",
    "4l1c3",
    "4dn3ss",
    "4rv3l",
]

print("[*] Testing possible middle words:\n")

for word in possible_words:
    # Try with just the word
    flag1 = f"Kaal{{l4yers_of_d3c03pt10n_m{word}_@sk_7h3_pr353nc3_0f_pO1s0ns}}"
    print(f"  {flag1}")
    
    # Try with m before @sk
    if word != "@sk":
        flag2 = f"Kaal{{l4yers_of_d3c03pt10n_m{word}_m@sk_7h3_pr353nc3_0f_pO1s0ns}}"
        print(f"  {flag2}")

print("\n[*] Most likely based on theme:")
print("  Kaal{l4yers_of_d3c03pt10n_mwh1sp3r_m@sk_7h3_pr353nc3_0f_pO1s0ns}")
print("  Kaal{l4yers_of_d3c03pt10n_mut3_m@sk_7h3_pr353nc3_0f_pO1s0ns}")
print("  Kaal{l4yers_of_d3c03pt10n_myst3ry_m@sk_7h3_pr353nc3_0f_pO1s0ns}")
