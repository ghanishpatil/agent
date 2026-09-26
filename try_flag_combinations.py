#!/usr/bin/env python3
"""
Try different flag combinations based on the headers
"""

prefix = "laak_de43e58e"
secret = "38h4vg6s45ch1lr19x4pe18s55r2kh1lx5331mh1mc5656w0"

print("="*70)
print("Possible Flag Combinations")
print("="*70)

# Extract parts
prefix_word = prefix.split('_')[0]  # "laak"
prefix_suffix = prefix.split('_')[1]  # "de43e58e"

print(f"\nPrefix word: {prefix_word}")
print(f"Prefix suffix: {prefix_suffix}")
print(f"Prefix reversed: {prefix_word[::-1]}")  # "kaal"
print(f"Secret: {secret}")

print(f"\n" + "="*70)
print("Flag Candidates:")
print("="*70)

candidates = [
    f"Kaal{{{secret}}}",
    f"Kaal{{{prefix_suffix}}}",
    f"Kaal{{{prefix}}}",
    f"Kaal{{{prefix_word}_{secret}}}",
    f"Kaal{{{prefix_suffix}_{secret}}}",
    f"Kaal{{md5_c0ll1s10n_{prefix_suffix}}}",
    f"Kaal{{t1m3_tr4v3l3r_{prefix_suffix}}}",
    f"Kaal{{c0ll1s10n_{prefix_suffix}}}",
]

for i, candidate in enumerate(candidates, 1):
    print(f"{i}. {candidate}")

# Maybe the challenge description gives a hint
print(f"\n" + "="*70)
print("Challenge Description Analysis:")
print("="*70)
print("'Time traveler's secret code broke'")
print("'Lost in time echoes'")
print("'Hidden in magic scroll'")
print("'Open last lock to get flag'")
print()
print("Keywords: time, echoes, scroll, lock")
print("Maybe: Kaal{t1m3_3ch03s_...} or Kaal{m4g1c_scr0ll_...}")

# Check if there's a pattern in the secret
print(f"\n" + "="*70)
print("Secret Analysis:")
print("="*70)
print(f"Secret: {secret}")
print(f"Length: {len(secret)}")
print(f"Looks like: random alphanumeric string")
print(f"Could be: session ID, hash, or encoded data")

# The hint said "fake flag is not useless"
# Maybe the X-Secret is a "fake flag" and we need to transform it
print(f"\n" + "="*70)
print("'Fake flag is not useless' - Transformations:")
print("="*70)

import hashlib

# MD5 of secret
md5_secret = hashlib.md5(secret.encode()).hexdigest()
print(f"MD5(secret): {md5_secret}")
print(f"  Flag: Kaal{{{md5_secret}}}")

# MD5 of prefix
md5_prefix = hashlib.md5(prefix.encode()).hexdigest()
print(f"MD5(prefix): {md5_prefix}")
print(f"  Flag: Kaal{{{md5_prefix}}}")

# Combine and hash
combined = prefix + secret
md5_combined = hashlib.md5(combined.encode()).hexdigest()
print(f"MD5(prefix+secret): {md5_combined}")
print(f"  Flag: Kaal{{{md5_combined}}}")
