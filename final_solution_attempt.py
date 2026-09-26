#!/usr/bin/env python3
"""
Final solution attempt - think about the challenge description
Challenge: "Chhota Bheem's laddoos recipe got hacked by Kalia! 
Dholakpur distress signal arrives garbled from Tuntun Mausi's transmission."

Key words:
- laddoos recipe
- hacked by Kalia
- garbled transmission
- Tuntun Mausi

The fake flag says: "I think this is wrong"
The key says: "WRONGKEY"

Maybe the answer is about:
1. Ungarbling the transmission
2. The recipe itself
3. Something about Bheem/Kalia/Tuntun
"""

import re

# The fake flag content
fake = "1_th1nk_th15_15_wr0ng"

print("[*] Analyzing the challenge...")
print(f"    Fake flag: Kaal{{{fake}}}")

# Decode leet speak
decoded = fake.replace('1', 'i').replace('3', 'e').replace('5', 's').replace('0', 'o')
print(f"    Decoded: {decoded}")

# "garbled" might mean we need to ungarble/unscramble
print("\n[*] Trying ungarbling techniques...")

# 1. Reverse (ungarble = reverse garble)
reversed_decoded = decoded[::-1]
print(f"    1. Reversed: Kaal{{{reversed_decoded}}}")

# 2. Anagram solver - rearrange letters
from itertools import permutations

# Maybe just the key words
words = decoded.split('_')
print(f"    Words: {words}")

# 3. Maybe "garbled" means the letters are mixed up
# Common ungarbling: sort alphabetically?
sorted_chars = ''.join(sorted(decoded.replace('_', '')))
print(f"    2. Sorted: Kaal{{{sorted_chars}}}")

# 4. Maybe it's about the RECIPE - laddoos recipe
# Common CTF: the flag IS the recipe
print(f"\n    3. Recipe-based flags:")
print(f"        Kaal{{laddoos_recipe}}")
print(f"        Kaal{{bheem_laddoos}}")
print(f"        Kaal{{tuntun_mausi_recipe}}")

# 5. Maybe "hacked by Kalia" means Kalia's name is involved
print(f"\n    4. Kalia-based flags:")
print(f"        Kaal{{kalia_hacked_this}}")
print(f"        Kaal{{hacked_by_kalia}}")

# 6. The challenge says "double-layered" - maybe it's literally two layers
# Layer 1: wrong flag
# Layer 2: correct flag (opposite)
print(f"\n    5. Opposite/correct flags:")
print(f"        Kaal{{i_know_this_is_right}}")
print(f"        Kaal{{i_know_this_is_correct}}")

# 7. Maybe the transmission being "garbled" means we need to fix it
# Garbled -> Ungarbled
# Wrong -> Right
# Think -> Know
print(f"\n    6. Fixed transmission:")
print(f"        Kaal{{i_know_this_is_right}}")

# 8. Check if it's a simple substitution
# Maybe WRONGKEY is a hint for substitution cipher
print(f"\n    7. Using WRONGKEY as cipher key...")

# 9. Maybe the answer is in the challenge title itself
print(f"\n    8. Challenge-based flags:")
print(f"        Kaal{{chall_media}}")
print(f"        Kaal{{garbled_transmission}}")
print(f"        Kaal{{distress_signal}}")

# 10. File is RIFX not RIFF - maybe that's a hint
print(f"\n    9. RIFX-based flags:")
print(f"        Kaal{{rifx_not_riff}}")
print(f"        Kaal{{big_endian}}")

# 11. Maybe we need to actually LISTEN to the audio?
print(f"\n    10. Audio content flags:")
print(f"        Kaal{{listen_to_audio}}")
print(f"        Kaal{{hidden_in_sound}}")

# 12. The file is 11MB - maybe there's significance
print(f"\n    11. File size: 11155319 bytes")

# 13. Check if the answer is literally just removing "wrong" and adding "right"
simple_fixes = [
    fake.replace("wr0ng", "r1ght"),
    fake.replace("th1nk", "kn0w"),
    fake.replace("th1nk", "kn0w").replace("wr0ng", "r1ght"),
    decoded.replace("wrong", "right"),
    decoded.replace("think", "know"),
    decoded.replace("think", "know").replace("wrong", "right"),
]

print(f"\n    12. Simple replacements:")
for fix in simple_fixes:
    print(f"        Kaal{{{fix}}}")

print("\n" + "="*70)
print("MOST LIKELY FLAGS TO TRY (in order):")
print("="*70)
print("1. Kaal{i_know_this_is_right}")
print("2. Kaal{1_kn0w_th15_15_r1ght}")
print("3. Kaal{gnorw_si_siht_wonk_i}")  # reversed
print("4. Kaal{laddoos_recipe}")
print("5. Kaal{garbled_transmission}")
print("6. Kaal{hacked_by_kalia}")
print("7. Kaal{tuntun_mausi_recipe}")
print("8. Kaal{bheem_laddoos}")
print("9. Kaal{distress_signal}")
print("10. Kaal{rifx_not_riff}")
