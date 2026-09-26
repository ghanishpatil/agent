#!/usr/bin/env python3
"""Final Spartans solution with correct filler logic"""

# The hint says: "Only remove the filler inserted between repeated letters
# —keep the one that naturally remains at the end."

# This means if we have AXA, we remove X and one A, keeping just A
# If we have AA at the end, we keep both

text = "MOOMXUTVHSKIIAHPM"

print("="*60)
print("ANALYZING: MOOMXUTVHSKIIAHPM")
print("="*60)

# Manual analysis
print("\nBreaking into pairs (Playfair works in pairs):")
pairs = [text[i:i+2] for i in range(0, len(text), 2)]
print(pairs)
print(" ".join(pairs))

# MO OM XU TV HS KI IA HP M
# Looking at this:
# MO-OM: This is M[O]M with O as filler
# KI-IA: Might be K[I]A with I as filler? Or just KI IA

print("\nRemoving fillers:")
print("MO OM -> M (O is filler between M-M)")
print("XU TV HS -> XUTVHS (no fillers)")
print("KI IA -> KIA or KA? (I might be filler)")
print("HP M -> HPM (no filler)")

# Let's try: MXUTVHSKIAHPM or MXUTVHSKAHPM
result1 = "MXUTVHSKIAHPM"
result2 = "MXUTVHSKAHPM"

print(f"\nPossible results:")
print(f"1. {result1}")
print(f"2. {result2}")

print(f"\nFlags:")
print(f"Kaal{{{result1.lower()}}}")
print(f"Kaal{{{result2.lower()}}}")

# Let's also check other candidates
print("\n" + "="*60)
print("OTHER CANDIDATES:")
print("="*60)

candidates = {
    "SPARTANS": "FUDRWMKXXTDIDDCPMR",
    "FRIENDS": "HKFAHPMWXXKIIASPO",
}

for key, dec in candidates.items():
    print(f"\n{key}: {dec}")
    pairs = [dec[i:i+2] for i in range(0, len(dec), 2)]
    print("Pairs:", " ".join(pairs))
    
    # Look for patterns like XX, where X is filler
    if "XX" in dec:
        print(f"  Has XX - might be filler")
        cleaned = dec.replace("XX", "X")
        print(f"  Cleaned: {cleaned}")
        print(f"  Flag: Kaal{{{cleaned.lower()}}}")

print("\n" + "="*60)
