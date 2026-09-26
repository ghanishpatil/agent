#!/usr/bin/env python3
"""
Extract the exact flag from the Hindi riddle
"""

print("="*80)
print("EXTRACTING EXACT FLAG")
print("="*80)

# Key clue from image: 42, 73, 99
numbers = [42, 73, 99]

print("\n[METHOD 1: ASCII Conversion]")
ascii_chars = ''.join([chr(n) for n in numbers])
print(f"Numbers {numbers} → ASCII: '{ascii_chars}'")
print(f"Possible flag: CTF{{{ascii_chars}}}")

print("\n[METHOD 2: Page Number Analysis]")
print("The code shows: mainText = fragments[page % fragments.length]")
print("With 8 fragments, the hint numbers map to:")
for num in numbers:
    idx = num % 8
    print(f"  Page {num} → Fragment index {idx}")

print("\n[METHOD 3: Looking at visible text]")
print("From image, I can see:")
print("  '_WRONG} का जिक्र ही सकता है!'")
print("  This suggests finding what's NOT wrong")

print("\n[METHOD 4: Combining clues]")
print("Fragment 4 says: 'छोटा इशारा: 42, 73, 99' (Small hint)")
print("Fragment 8 says: '🚩 असली निशान कधी ओर है' (Real flag is elsewhere)")
print()
print("The numbers might be:")
print("  - Character codes")
print("  - Page numbers to visit")
print("  - Indices to extract from fragments")

# Try different interpretations
print("\n" + "="*80)
print("POSSIBLE FLAGS:")
print("="*80)

flags = [
    "CTF{*Ic}",  # Direct ASCII
    "CTF{42_73_99}",  # Numbers themselves
    "CTF{MARATHI}",  # Language hint
    "CTF{HINDI}",  # Language hint
    "CTF{100_PAGES}",  # Mentioned in fragments
    "CTF{REAL_FLAG}",  # Opposite of NOT_A_FLAG
    "CTF{IGNORE_NOTHING}",  # Opposite of IGNORE_ME
]

for i, flag in enumerate(flags, 1):
    print(f"{i}. {flag}")

print("\n" + "="*80)
print("MOST LIKELY FLAG:")
print("="*80)

# Based on CTF patterns and the ASCII hint
print("""
Given the clues:
1. Numbers 42, 73, 99 are explicitly called "छोटा इशारा" (small hint)
2. ASCII conversion: * I c
3. The pattern of fake flags suggests the real one is hidden

The most likely flag is:
""")

print("\n🚩 CTF{*Ic} or CTF{42_73_99}")

print("\n" + "="*80)
print("TO GET EXACT FLAG:")
print("="*80)
print("""
I need the website URL to:
1. Visit page 42, 73, and 99
2. Check the actual JavaScript source
3. Test the flag submission

Please provide the URL or tell me which of these flags is correct!
""")
