#!/usr/bin/env python3
"""
Complete Westeros solver - try all encoding methods
"""

# Part 1: ASCII decimal
part1 = ''.join(chr(d) for d in [74, 111, 48, 104, 53])
print(f"Part 1: {part1}")

# Part 2: Bacon cipher
bacon = {'abaaa': 'I', 'baaab': 'R'}
part2 = 'IR'
print(f"Part 2: {part2}")

# Part 3: Japanese hiragana
# り (ri) ち (chi) し (shi) し (shi) い (i) す (su)
# Could this spell "riches" or something else?
part3_chars = "りちししいす"
print(f"Part 3 raw: {part3_chars}")

# Standard romaji
romaji_standard = "richishishiisu"
print(f"Part 3 romaji: {romaji_standard}")

# Try different interpretations
# り=ri, ち=chi, し=shi, い=i, す=su
# But what if it's meant to be read as English phonetically?
# ri-chi-shi-shi-i-su could be "riches" + "isu"?

# Or maybe the hiragana needs to be decoded differently
# Let's try: each hiragana character position in alphabet?
hiragana_order = {
    'あ': 1, 'い': 2, 'う': 3, 'え': 4, 'お': 5,
    'か': 6, 'き': 7, 'く': 8, 'け': 9, 'こ': 10,
    'さ': 11, 'し': 12, 'す': 13, 'せ': 14, 'そ': 15,
    'た': 16, 'ち': 17, 'つ': 18, 'て': 19, 'と': 20,
    'な': 21, 'に': 22, 'ぬ': 23, 'ね': 24, 'の': 25,
    'は': 26, 'ひ': 27, 'ふ': 28, 'へ': 29, 'ほ': 30,
    'ま': 31, 'み': 32, 'む': 33, 'め': 34, 'も': 35,
    'や': 36, 'ゆ': 37, 'よ': 38,
    'ら': 39, 'り': 40, 'る': 41, 'れ': 42, 'ろ': 43,
    'わ': 44, 'を': 45, 'ん': 46
}

# Check if it's a substitution cipher
# Game of Thrones famous quote: "Winter is Coming"
# Let's see if the parts spell that

print("\n" + "="*60)
print("Testing famous GoT quotes:")
print("Winter is Coming")
print("Valar Morghulis")
print("A Lannister always pays his debts")
print("="*60)

# Maybe the Japanese is just phonetic English?
# り (ri) ち (ti/chi) し (si/shi) し (si/shi) い (i) す (su)
# Could be: "riches" or "richis" or something

# Let's try all combinations
print("\nAll flag attempts:")
flags = [
    f"Kaal{{Jo0h5_IR_richishishiisu}}",
    f"Kaal{{Jo0h5_ir_richishishiisu}}",
    f"Kaal{{jo0h5_ir_richishishiisu}}",
    f"Kaal{{John_is_riches}}",  # Wild guess
    f"Kaal{{Jo0h5_IS_richishishiisu}}",  # Maybe IR -> IS?
]

for i, flag in enumerate(flags, 1):
    print(f"{i}. {flag}")
